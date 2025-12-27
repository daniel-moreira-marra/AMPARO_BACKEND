from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status

from ..serializers import TokenByEmailSerializer


def token_by_email_docs():
    """
    Retorna o decorator `extend_schema` pronto para ser aplicado na view.

    Uso:
        @token_by_email_docs()
        def post(...):
            ...
    """
    return extend_schema(
        tags=["Auth"],
        summary="Login (JWT) por e-mail",
        description=(
            "Autentica o usuário utilizando e-mail e senha, "
            "e retorna tokens JWT."
        ),
        request=TokenByEmailSerializer,
        responses={status.HTTP_200_OK: TokenByEmailSerializer,
                   status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Credenciais inválidas.")},
    )