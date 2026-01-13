from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    ParseError,
    ValidationError,
    PermissionDenied,
    NotAuthenticated,
)
from rest_framework import status

from .responses import error_response
from .codes import ErrorCode

def deny_role(required_role: str):
    """
    Lança PermissionDenied com mensagem padronizada
    para uso quando o usuário não tem o role esperado.
    """
    raise PermissionDenied(
        f"Apenas usuários do tipo {required_role} podem acessar este endpoint."
    )



def custom_exception_handler(exc, context):
    """
    Handler global de exceções da API.
    Intercepta erros do DRF e padroniza o formato de resposta.
    """
    # Primeiro deixa o DRF processar
    response = exception_handler(exc, context)

    # JSON malformado
    if isinstance(exc, ParseError):
        return error_response(
            code=ErrorCode.INVALID_JSON,
            message="Payload inválido. Verifique se o JSON está bem formatado.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # Erros de validação (serializers)
    if isinstance(exc, ValidationError):
        return error_response(
            code=ErrorCode.VALIDATION_ERROR,
            message="Erro de validação nos dados enviados.",
            details=exc.detail,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # Não autenticado
    if isinstance(exc, NotAuthenticated):
        return error_response(
            code=ErrorCode.NOT_AUTHENTICATED,
            message="Autenticação necessária para acessar este recurso.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    # Sem permissão
    if isinstance(exc, PermissionDenied):
        return error_response(
            code=ErrorCode.PERMISSION_DENIED,
            message=str(exc.detail),  # preserva a mensagem do deny_role
            status_code=status.HTTP_403_FORBIDDEN,
        )


    # Se o DRF já gerou uma resposta, apenas retorna
    if response is not None:
        return response

    # Erro inesperado (500)
    return error_response(
        code=ErrorCode.SERVER_ERROR,
        message="Erro interno do servidor.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
