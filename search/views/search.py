from django.db.models import Q
from rest_framework import status
from rest_framework.views import APIView

from accounts.models import (
    ElderProfile,
    GuardianProfile,
    CaregiverProfile,
    ProfessionalProfile,
    InstitutionProfile,
)
from core.exceptions.responses import success_response, error_response

from ..serializers import (
    ElderSearchSerializer,
    GuardianSearchSerializer,
    CaregiverSearchSerializer,
    ProfessionalSearchSerializer,
    InstitutionSearchSerializer,
)
from ..docs import search_get_docs


VALID_ROLES = ["ELDER", "GUARDIAN", "CAREGIVER", "PROFESSIONAL", "INSTITUTION"]


def _search_elders(q: str, params: dict) -> list:
    qs = ElderProfile.objects.select_related("user").filter(user__is_active=True)
    if q:
        qs = qs.filter(
            Q(user__full_name__icontains=q) | Q(preferred_name__icontains=q)
        )
    city = params.get("city", "").strip()
    if city:
        qs = qs.filter(user__city__icontains=city)
    state = params.get("state", "").strip()
    if state:
        qs = qs.filter(user__state__iexact=state)
    return ElderSearchSerializer(qs, many=True).data


def _search_guardians(q: str, params: dict) -> list:
    qs = GuardianProfile.objects.select_related("user").filter(user__is_active=True)
    if q:
        qs = qs.filter(Q(user__full_name__icontains=q))
    city = params.get("city", "").strip()
    if city:
        qs = qs.filter(user__city__icontains=city)
    state = params.get("state", "").strip()
    if state:
        qs = qs.filter(user__state__iexact=state)
    return GuardianSearchSerializer(qs, many=True).data


def _search_caregivers(q: str, params: dict) -> list:
    qs = CaregiverProfile.objects.select_related("user").filter(user__is_active=True)
    if q:
        qs = qs.filter(
            Q(user__full_name__icontains=q) | Q(bio__icontains=q)
        )
    city = params.get("city", "").strip()
    if city:
        qs = qs.filter(Q(city__icontains=city) | Q(user__city__icontains=city))
    state = params.get("state", "").strip()
    if state:
        qs = qs.filter(Q(state__iexact=state) | Q(user__state__iexact=state))
        
    is_available = params.get("is_available")
    if is_available is not None:
        if str(is_available).lower() in ['true', '1', 't', 'y', 'yes', 'on']:
            qs = qs.filter(is_available=True)
        elif str(is_available).lower() in ['false', '0', 'f', 'n', 'no', 'off']:
            qs = qs.filter(is_available=False)
            
    experience_years = params.get("experience_years")
    if experience_years:
        try:
           qs = qs.filter(experience_years__gte=int(experience_years))
        except (ValueError, TypeError):
           pass
    return CaregiverSearchSerializer(qs, many=True).data


def _search_professionals(q: str, params: dict) -> list:
    qs = ProfessionalProfile.objects.select_related("user").filter(user__is_active=True)
    if q:
        qs = qs.filter(
            Q(user__full_name__icontains=q)
            | Q(bio__icontains=q)
            | Q(profession__icontains=q)
        )
    city = params.get("city", "").strip()
    if city:
        qs = qs.filter(Q(city__icontains=city) | Q(user__city__icontains=city))
    state = params.get("state", "").strip()
    if state:
        qs = qs.filter(Q(state__iexact=state) | Q(user__state__iexact=state))
        
    is_available = params.get("is_available")
    if is_available is not None:
        if str(is_available).lower() in ['true', '1', 't', 'y', 'yes', 'on']:
            qs = qs.filter(is_available=True)
        elif str(is_available).lower() in ['false', '0', 'f', 'n', 'no', 'off']:
            qs = qs.filter(is_available=False)
            
    profession = params.get("profession", "").strip()
    if profession:
        qs = qs.filter(profession__iexact=profession)
        
    service_mode = params.get("service_mode", "").strip()
    if service_mode:
        qs = qs.filter(service_mode__iexact=service_mode)

    min_price = params.get("min_price")
    if min_price is not None:
        try:
           qs = qs.filter(hourly_rate__gte=float(min_price))
        except (ValueError, TypeError):
           pass
           
    max_price = params.get("max_price")
    if max_price is not None:
        try:
           qs = qs.filter(hourly_rate__lte=float(max_price))
        except (ValueError, TypeError):
           pass
    return ProfessionalSearchSerializer(qs, many=True).data


def _search_institutions(q: str, params: dict) -> list:
    qs = InstitutionProfile.objects.select_related("user").filter(user__is_active=True)
    if q:
        qs = qs.filter(
            Q(user__full_name__icontains=q)
            | Q(legal_name__icontains=q)
            | Q(trade_name__icontains=q)
        )
    city = params.get("city", "").strip()
    if city:
        qs = qs.filter(user__city__icontains=city)
    state = params.get("state", "").strip()
    if state:
        qs = qs.filter(user__state__iexact=state)
    return InstitutionSearchSerializer(qs, many=True).data


_ROLE_HANDLERS = {
    "ELDER": _search_elders,
    "GUARDIAN": _search_guardians,
    "CAREGIVER": _search_caregivers,
    "PROFESSIONAL": _search_professionals,
    "INSTITUTION": _search_institutions,
}


class SearchView(APIView):
    """
    GET /api/v1/search – Busca de contas por tipo e/ou texto livre.

    Query params:
        role (str, opcional): Filtrar por tipo de conta.
                              Aceita: ELDER, GUARDIAN, CAREGIVER, PROFESSIONAL, INSTITUTION.
        q    (str, opcional): Texto a pesquisar em campos relevantes ao tipo.

    Retorno quando `role` é informado:
        { "success": true, "data": { "role": "PROFESSIONAL", "count": N, "results": [...] } }

    Retorno quando `role` é omitido (lista plana com discriminador `role` por item):
        { "success": true, "data": { "count": N, "results": [...] } }
    """

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

        if role:
            handler = _ROLE_HANDLERS[role]
            results = handler(q, request.query_params)
            return success_response(
                data={
                    "role": role,
                    "count": len(results),
                    "results": results,
                }
            )

        # Busca em todos os tipos → lista plana
        all_results = []
        for r, handler in _ROLE_HANDLERS.items():
            all_results.extend(handler(q, request.query_params))

        return success_response(
            data={
                "count": len(all_results),
                "results": all_results,
            }
        )
