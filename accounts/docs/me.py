"""
Documentacao Swagger/OpenAPI para a rota /me.

Requer: drf-spectacular
- pip install drf-spectacular
- Configure o DEFAULT_SCHEMA_CLASS no settings.py.
"""

from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status

from ..serializers import MeSerializer


def me_docs():
    """
    Retorna o decorator `extend_schema` pronto para ser aplicado na view.

    Uso:
        @me_docs()
        def get(...):
            ...
    """
    return extend_schema(
        tags=["Auth"],
        summary="Dados do usuario logado",
        description=(
            "Retorna os dados do usuario autenticado. "
            "Requer autenticacao JWT."
        ),
        responses={
            status.HTTP_200_OK: MeSerializer,
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description="Nao autenticado"),
        },
    )
