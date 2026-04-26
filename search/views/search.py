from django.db.models import Q
from rest_framework import status
from rest_framework.views import APIView

from accounts.models import User
from core.exceptions.responses import success_response, error_response
from core.pagination import SearchPagination

from ..serializers import (
    ElderSearchSerializer,
    GuardianSearchSerializer,
    CaregiverSearchSerializer,
    ProfessionalSearchSerializer,
    InstitutionSearchSerializer,
)
from ..docs import search_get_docs


VALID_ROLES = ["ELDER", "GUARDIAN", "CAREGIVER", "PROFESSIONAL", "INSTITUTION"]


def _build_elders_q(q: str, params: dict) -> Q:
    query = Q(role="ELDER")
    if q:
        query &= (Q(full_name__icontains=q) | Q(elder_profile__preferred_name__icontains=q))
    city = params.get("city", "").strip()
    if city:
        query &= Q(city__icontains=city)
    state = params.get("state", "").strip()
    if state:
        query &= Q(state__iexact=state)
    return query


def _build_guardians_q(q: str, params: dict) -> Q:
    query = Q(role="GUARDIAN")
    if q:
        query &= Q(full_name__icontains=q)
    city = params.get("city", "").strip()
    if city:
        query &= Q(city__icontains=city)
    state = params.get("state", "").strip()
    if state:
        query &= Q(state__iexact=state)
    return query


def _build_caregivers_q(q: str, params: dict) -> Q:
    query = Q(role="CAREGIVER")
    if q:
        query &= (Q(full_name__icontains=q) | Q(caregiver_profile__bio__icontains=q))
    city = params.get("city", "").strip()
    if city:
        query &= (Q(caregiver_profile__city__icontains=city) | Q(city__icontains=city))
    state = params.get("state", "").strip()
    if state:
        query &= (Q(caregiver_profile__state__iexact=state) | Q(state__iexact=state))
        
    is_available = params.get("is_available")
    if is_available is not None:
        if str(is_available).lower() in ['true', '1', 't', 'y', 'yes', 'on']:
            query &= Q(caregiver_profile__is_available=True)
        elif str(is_available).lower() in ['false', '0', 'f', 'n', 'no', 'off']:
            query &= Q(caregiver_profile__is_available=False)
            
    experience_years = params.get("experience_years")
    if experience_years:
        try:
           query &= Q(caregiver_profile__experience_years__gte=int(experience_years))
        except (ValueError, TypeError):
           pass
    return query


def _build_professionals_q(q: str, params: dict) -> Q:
    query = Q(role="PROFESSIONAL")
    if q:
        query &= (
            Q(full_name__icontains=q)
            | Q(professional_profile__bio__icontains=q)
            | Q(professional_profile__profession__icontains=q)
        )
    city = params.get("city", "").strip()
    if city:
        query &= (Q(professional_profile__city__icontains=city) | Q(city__icontains=city))
    state = params.get("state", "").strip()
    if state:
        query &= (Q(professional_profile__state__iexact=state) | Q(state__iexact=state))
        
    is_available = params.get("is_available")
    if is_available is not None:
        if str(is_available).lower() in ['true', '1', 't', 'y', 'yes', 'on']:
            query &= Q(professional_profile__is_available=True)
        elif str(is_available).lower() in ['false', '0', 'f', 'n', 'no', 'off']:
            query &= Q(professional_profile__is_available=False)
            
    profession = params.get("profession", "").strip()
    if profession:
        query &= Q(professional_profile__profession__iexact=profession)
        
    service_mode = params.get("service_mode", "").strip()
    if service_mode:
        query &= Q(professional_profile__service_mode__iexact=service_mode)

    min_price = params.get("min_price")
    if min_price is not None:
        try:
           query &= Q(professional_profile__hourly_rate__gte=float(min_price))
        except (ValueError, TypeError):
           pass
           
    max_price = params.get("max_price")
    if max_price is not None:
        try:
           query &= Q(professional_profile__hourly_rate__lte=float(max_price))
        except (ValueError, TypeError):
           pass
    return query


def _build_institutions_q(q: str, params: dict) -> Q:
    query = Q(role="INSTITUTION")
    if q:
        query &= (
            Q(full_name__icontains=q)
            | Q(institution_profile__legal_name__icontains=q)
            | Q(institution_profile__trade_name__icontains=q)
        )
    city = params.get("city", "").strip()
    if city:
        query &= Q(city__icontains=city)
    state = params.get("state", "").strip()
    if state:
        query &= Q(state__iexact=state)
    return query


_ROLE_Q_BUILDERS = {
    "ELDER": _build_elders_q,
    "GUARDIAN": _build_guardians_q,
    "CAREGIVER": _build_caregivers_q,
    "PROFESSIONAL": _build_professionals_q,
    "INSTITUTION": _build_institutions_q,
}


_ROLE_ATTR = {
    "ELDER":        ("elder_profile",        ElderSearchSerializer),
    "GUARDIAN":     ("guardian_profile",     GuardianSearchSerializer),
    "CAREGIVER":    ("caregiver_profile",    CaregiverSearchSerializer),
    "PROFESSIONAL": ("professional_profile", ProfessionalSearchSerializer),
    "INSTITUTION":  ("institution_profile",  InstitutionSearchSerializer),
}


def _fallback_user_data(user) -> dict:
    """Minimal card data for users whose role profile hasn't been created yet."""
    return {
        "id": None,
        "user_id": user.id,
        "role": user.role,
        "full_name": user.full_name,
        "city": user.city,
        "state": user.state,
    }


def _serialize_for_role(user) -> dict:
    config = _ROLE_ATTR.get(user.role)
    if not config:
        return _fallback_user_data(user)
    attr, serializer_class = config
    profile = getattr(user, attr, None)
    return serializer_class(profile).data if profile else _fallback_user_data(user)


class SearchView(APIView):
    """
    GET /api/v1/search – Busca de contas por tipo e/ou texto livre.

    Query params:
        role (str, opcional): Filtrar por tipo de conta.
                              Aceita: ELDER, GUARDIAN, CAREGIVER, PROFESSIONAL, INSTITUTION.
        q    (str, opcional): Texto a pesquisar em campos relevantes ao tipo.

    Retorna resultados paginados (limit-offset, default 100).
    """

    pagination_class = SearchPagination

    @search_get_docs()
    def get(self, request):
        role = request.query_params.get("role", "").strip().upper() or None
        q = request.query_params.get("q", "").strip()

        # Validar role, se fornecido
        if role and role not in VALID_ROLES:
            return error_response(
                code="INVALID_ROLE",
                message=(
                    f"Role '{role}' inválido. "
                    f"Valores aceitos: {', '.join(VALID_ROLES)}."
                ),
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        base_query = Q(is_active=True)
        if role:
            base_query &= _ROLE_Q_BUILDERS[role](q, request.query_params)
        else:
            # Explicit role whitelist — avoids empty-Q OR ambiguity
            base_query &= Q(role__in=VALID_ROLES)
            if q:
                base_query &= (
                    Q(full_name__icontains=q)
                    | Q(elder_profile__preferred_name__icontains=q)
                    | Q(caregiver_profile__bio__icontains=q)
                    | Q(professional_profile__bio__icontains=q)
                    | Q(professional_profile__profession__icontains=q)
                    | Q(institution_profile__legal_name__icontains=q)
                    | Q(institution_profile__trade_name__icontains=q)
                )

        users_qs = User.objects.filter(base_query).select_related(
            "elder_profile",
            "guardian_profile",
            "caregiver_profile",
            "professional_profile",
            "institution_profile",
        ).distinct().order_by("full_name")

        paginator = self.pagination_class()
        paginated_users = paginator.paginate_queryset(users_qs, request, view=self)
        
        results = []
        if paginated_users is not None:
            for user in paginated_users:
                results.append(_serialize_for_role(user))

        data = {
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link(),
            "results": results,
        }
        if role:
            data["role"] = role

        return success_response(data=data)
