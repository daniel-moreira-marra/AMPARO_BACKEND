"""
Documentacao Swagger/OpenAPI para a rota /me.

Requer: drf-spectacular
- pip install drf-spectacular
- Configure o DEFAULT_SCHEMA_CLASS no settings.py.
"""

from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status

from ..serializers import SignupSerializer, SignupResponseSerializer


def signup_docs():
    """
    Retorna o decorator `extend_schema` pronto para ser aplicado na view.

    Uso:
        @signup_docs()
        def post(...):
            ...
    """
    return extend_schema(
        tags=["Auth"],
        summary="Cadastro de usuário",
        description=(
            "Cria um novo usuário no sistema. "
            "Não requer autenticação."
        ),
        request=SignupSerializer,
        responses={
            status.HTTP_201_CREATED: SignupResponseSerializer,
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Dados invalidos"),
        },
    )
