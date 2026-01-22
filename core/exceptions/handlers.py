from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException, ParseError
from rest_framework import status

from .responses import error_response
from .codes import ErrorCode
from .helpers import _stringify_error_detail

def custom_exception_handler(exc, context):
    # print("EXC TYPE:", type(exc))
    # print("EXC REPR:", repr(exc))
    # print("EXC DETAIL:", getattr(exc, "detail", None))

    response = exception_handler(exc, context)

    # JSON malformado (mensagem amigável)
    if isinstance(exc, ParseError):
        return error_response(
            code=ErrorCode.INVALID_JSON,
            message="Payload inválido. Verifique se o JSON está bem formatado.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    # Qualquer exceção do DRF (preserva status code)
    if isinstance(exc, APIException):
        if exc.status_code == 400:
            code = ErrorCode.VALIDATION_ERROR
            details = exc.detail
            message = "Erro de validação nos dados enviados."
        elif exc.status_code == 401:
            code = ErrorCode.NOT_AUTHENTICATED
            details = None
            message = _stringify_error_detail(getattr(exc, "detail", "Autenticação necessária."))
        elif exc.status_code == 403:
            code = ErrorCode.PERMISSION_DENIED
            details = None
            message = str(getattr(exc, "detail", "Sem permissão."))
        elif exc.status_code == 404:
            code = ErrorCode.NOT_FOUND
            details = None
            message = str(getattr(exc, "detail", "Recurso não encontrado."))
        else:
            code = ErrorCode.SERVER_ERROR
            details = None
            message = str(getattr(exc, "detail", "Erro na requisição."))

        return error_response(
            code=code,
            message=message,
            details=details,
            status_code=exc.status_code,
        )

    # Se DRF já gerou resposta (ex.: Http404 convertido), retorna
    if response is not None:
        return response

    # fallback 500
    return error_response(
        code=ErrorCode.SERVER_ERROR,
        message="Erro interno do servidor.",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
