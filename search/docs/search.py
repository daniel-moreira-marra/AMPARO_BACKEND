from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework import serializers

from core.docs.schemas import get_success_response_serializer, ERROR_401_UNAUTHORIZED


VALID_ROLES = ["ELDER", "GUARDIAN", "CAREGIVER", "PROFESSIONAL", "INSTITUTION"]


class SearchResultSerializer(serializers.Serializer):
    """Schema genérico representando um item de resultado de busca.
    Os campos reais variam conforme o `role` do resultado."""
    id = serializers.IntegerField(help_text="ID do perfil de papel (ElderProfile, CaregiverProfile, etc.).")
    user_id = serializers.IntegerField(help_text="ID do usuário.")
    role = serializers.ChoiceField(choices=VALID_ROLES, help_text="Papel do usuário.")
    full_name = serializers.CharField(help_text="Nome completo.")
    # ELDER
    preferred_name = serializers.CharField(allow_null=True, required=False, help_text="[ELDER] Nome preferido.")
    gender = serializers.CharField(allow_null=True, required=False, help_text="[ELDER] Gênero (MALE, FEMALE, OTHER, NOT_INFORMED).")
    mobility_level = serializers.CharField(allow_null=True, required=False, help_text="[ELDER] Nível de mobilidade.")
    # CAREGIVER
    bio = serializers.CharField(allow_null=True, required=False, help_text="[CAREGIVER/PROFESSIONAL] Bio.")
    experience_years = serializers.IntegerField(allow_null=True, required=False, help_text="[CAREGIVER] Anos de experiência.")
    is_available = serializers.BooleanField(required=False, help_text="[CAREGIVER/PROFESSIONAL] Disponível para novos vínculos.")
    city = serializers.CharField(allow_null=True, required=False, help_text="[CAREGIVER/PROFESSIONAL/INSTITUTION] Cidade.")
    state = serializers.CharField(allow_null=True, required=False, help_text="[CAREGIVER/PROFESSIONAL/INSTITUTION] Estado (UF).")
    # GUARDIAN
    relationship = serializers.CharField(allow_null=True, required=False, help_text="[GUARDIAN] Tipo de parentesco.")
    is_legal_guardian = serializers.BooleanField(required=False, help_text="[GUARDIAN] Se é responsável legal.")
    # PROFESSIONAL
    profession = serializers.CharField(allow_null=True, required=False, help_text="[PROFESSIONAL] Código da profissão.")
    profession_display = serializers.CharField(allow_null=True, required=False, help_text="[PROFESSIONAL] Nome legível da profissão.")
    profession_other = serializers.CharField(allow_null=True, required=False, help_text="[PROFESSIONAL] Profissão livre (quando profession=OTHER).")
    service_mode = serializers.CharField(allow_null=True, required=False, help_text="[PROFESSIONAL] Modalidade (HOME, CLINIC, ONLINE, OTHER).")
    hourly_rate = serializers.DecimalField(allow_null=True, required=False, max_digits=10, decimal_places=2, help_text="[PROFESSIONAL] Valor por hora.")
    registration_verified = serializers.BooleanField(required=False, help_text="[PROFESSIONAL] Registro profissional verificado.")
    # INSTITUTION
    legal_name = serializers.CharField(allow_null=True, required=False, help_text="[INSTITUTION] Razão social.")
    trade_name = serializers.CharField(allow_null=True, required=False, help_text="[INSTITUTION] Nome fantasia.")
    institution_type = serializers.CharField(allow_null=True, required=False, help_text="[INSTITUTION] Tipo (ILPI, SHELTER, CLINIC, HOSPITAL, OTHER).")
    is_verified = serializers.BooleanField(required=False, help_text="[INSTITUTION] Instituição verificada pela plataforma.")


class SearchPaginatedSerializer(serializers.Serializer):
    next = serializers.URLField(allow_null=True, help_text="URL da próxima página.")
    previous = serializers.URLField(allow_null=True, help_text="URL da página anterior.")
    results = SearchResultSerializer(many=True)
    role = serializers.CharField(required=False, help_text="Papel filtrado (presente apenas quando `role` foi passado como parâmetro).")


def search_get_docs():
    """
    Decorator extend_schema para o endpoint GET /api/v1/search.

    Uso:
        @search_get_docs()
        def get(self, request):
            ...
    """
    return extend_schema(
        tags=["Busca"],
        summary="Buscar usuários na plataforma",
        description=(
            "Pesquisa usuários cadastrados na plataforma por papel e/ou texto livre.\n\n"
            "**Paginação:** cursor-based — use o campo `next` da resposta para obter a próxima página.\n\n"
            "**Campos de resultado:** variam conforme o `role` de cada item. "
            "Campos de outros papéis estarão ausentes (não retornam como `null`, simplesmente não existem).\n\n"
            "**Enums relevantes:**\n"
            "- `profession`: `PHYSIOTHERAPIST`, `SPEECH_THERAPIST`, `OCCUPATIONAL_THERAPIST`, "
            "`PSYCHOLOGIST`, `NUTRITIONIST`, `OTHER`\n"
            "- `service_mode`: `HOME`, `CLINIC`, `ONLINE`, `OTHER`\n"
            "- `institution_type`: `ILPI`, `SHELTER`, `CLINIC`, `HOSPITAL`, `OTHER`\n"
            "- `mobility_level`: `INDEPENDENT`, `NEEDS_ASSISTANCE`, `WHEELCHAIR`, `BEDRIDDEN`\n"
            "- `gender`: `MALE`, `FEMALE`, `OTHER`, `NOT_INFORMED`"
        ),
        parameters=[
            OpenApiParameter(
                name="role",
                location=OpenApiParameter.QUERY,
                description=(
                    "Tipo de conta a filtrar. "
                    "Quando omitido, todos os tipos são retornados."
                ),
                required=False,
                type=str,
                enum=VALID_ROLES,
            ),
            OpenApiParameter(
                name="q",
                location=OpenApiParameter.QUERY,
                description=(
                    "Termo de busca textual. "
                    "Pesquisa em nome, bio, profissão ou razão social conforme o tipo de conta."
                ),
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="city",
                location=OpenApiParameter.QUERY,
                description="Filtrar por cidade (busca parcial, case-insensitive).",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="state",
                location=OpenApiParameter.QUERY,
                description="Filtrar por estado — UF exata (ex: SP, RJ).",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="is_available",
                location=OpenApiParameter.QUERY,
                description="Filtrar cuidadores ou profissionais disponíveis (true/false).",
                required=False,
                type=bool,
            ),
            OpenApiParameter(
                name="experience_years",
                location=OpenApiParameter.QUERY,
                description="Filtrar cuidadores com no mínimo N anos de experiência.",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="profession",
                location=OpenApiParameter.QUERY,
                description=(
                    "Filtrar profissionais por profissão exata. "
                    "Valores: PHYSIOTHERAPIST, SPEECH_THERAPIST, OCCUPATIONAL_THERAPIST, "
                    "PSYCHOLOGIST, NUTRITIONIST, OTHER."
                ),
                required=False,
                type=str,
                enum=["PHYSIOTHERAPIST", "SPEECH_THERAPIST", "OCCUPATIONAL_THERAPIST", "PSYCHOLOGIST", "NUTRITIONIST", "OTHER"],
            ),
            OpenApiParameter(
                name="service_mode",
                location=OpenApiParameter.QUERY,
                description="Filtrar profissionais por modalidade de atendimento (HOME, CLINIC, ONLINE, OTHER).",
                required=False,
                type=str,
                enum=["HOME", "CLINIC", "ONLINE", "OTHER"],
            ),
            OpenApiParameter(
                name="min_price",
                location=OpenApiParameter.QUERY,
                description="Filtrar profissionais com valor/hora ≥ este valor.",
                required=False,
                type=float,
            ),
            OpenApiParameter(
                name="max_price",
                location=OpenApiParameter.QUERY,
                description="Filtrar profissionais com valor/hora ≤ este valor.",
                required=False,
                type=float,
            ),
            OpenApiParameter(
                name="cursor",
                location=OpenApiParameter.QUERY,
                description="Token de paginação. Use o valor do campo `next` da resposta anterior.",
                required=False,
                type=str,
            ),
        ],
        responses={
            200: get_success_response_serializer(SearchPaginatedSerializer),
            401: ERROR_401_UNAUTHORIZED,
        },
        examples=[
            OpenApiExample(
                "Buscar cuidadores disponíveis em SP",
                description="GET /api/v1/search/?role=CAREGIVER&state=SP&is_available=true",
                value={
                    "success": True,
                    "data": {
                        "next": None,
                        "previous": None,
                        "role": "CAREGIVER",
                        "results": [
                            {
                                "id": 4,
                                "user_id": 7,
                                "role": "CAREGIVER",
                                "full_name": "Carlos Andrade",
                                "bio": "Cuidador especializado em Alzheimer.",
                                "experience_years": 5,
                                "city": "São Paulo",
                                "state": "SP",
                                "is_available": True,
                            }
                        ],
                    },
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Buscar fisioterapeutas com atendimento domiciliar",
                description="GET /api/v1/search/?role=PROFESSIONAL&profession=PHYSIOTHERAPIST&service_mode=HOME",
                value={
                    "success": True,
                    "data": {
                        "next": None,
                        "previous": None,
                        "role": "PROFESSIONAL",
                        "results": [
                            {
                                "id": 2,
                                "user_id": 9,
                                "role": "PROFESSIONAL",
                                "full_name": "Dra. Fernanda Lima",
                                "profession": "PHYSIOTHERAPIST",
                                "profession_display": "Fisioterapeuta",
                                "bio": "Especializada em reabilitação geriátrica.",
                                "service_mode": "HOME",
                                "hourly_rate": "150.00",
                                "is_available": True,
                                "registration_verified": True,
                                "city": "São Paulo",
                                "state": "SP",
                            }
                        ],
                    },
                },
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
