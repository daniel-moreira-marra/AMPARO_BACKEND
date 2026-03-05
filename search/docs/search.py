from drf_spectacular.utils import extend_schema, OpenApiParameter


VALID_ROLES = ["ELDER", "GUARDIAN", "CAREGIVER", "PROFESSIONAL", "INSTITUTION"]


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
        summary="Buscar contas",
        description=(
            "Pesquisa contas cadastradas na plataforma. "
            "Use `role` para filtrar por tipo de conta e `q` para busca textual. "
            "Quando `role` é omitido, todos os tipos são retornados em lista plana "
            "com um campo `role` discriminador em cada item."
        ),
        parameters=[
            OpenApiParameter(
                name="role",
                location=OpenApiParameter.QUERY,
                description=(
                    "Tipo de conta a filtrar. "
                    "Valores aceitos: ELDER, GUARDIAN, CAREGIVER, PROFESSIONAL, INSTITUTION."
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
                description="Filtrar perfis pela cidade.",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="state",
                location=OpenApiParameter.QUERY,
                description="Filtrar perfis pelo estado (ex: SP, RJ).",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="is_available",
                location=OpenApiParameter.QUERY,
                description="Filtrar profissionais ou cuidadores por disponibilidade (true/false).",
                required=False,
                type=bool,
            ),
            OpenApiParameter(
                name="experience_years",
                location=OpenApiParameter.QUERY,
                description="Filtrar cuidadores por anos de experiência (mínimo).",
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name="profession",
                location=OpenApiParameter.QUERY,
                description="Filtrar profissionais por profissão exata (ex: PHYSIOTHERAPIST).",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="service_mode",
                location=OpenApiParameter.QUERY,
                description="Filtrar profissionais por modalidade de atendimento (ex: HOME, REMOTE).",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="min_price",
                location=OpenApiParameter.QUERY,
                description="Filtrar profissionais por preço por hora mínimo.",
                required=False,
                type=float,
            ),
            OpenApiParameter(
                name="max_price",
                location=OpenApiParameter.QUERY,
                description="Filtrar profissionais por preço por hora máximo.",
                required=False,
                type=float,
            ),
        ],
        responses={200: None},
    )
