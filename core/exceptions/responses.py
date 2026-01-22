from rest_framework.response import Response


def error_response(*, code: str, message: str, status_code: int, details=None):
    """
    Gera uma resposta de erro padronizada para a API.
    """
    return Response(
        {
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details,
            }
        },
        status=status_code,
    )


def success_response(*, data, status_code: int = 200, headers=None):
    """
    Gera uma resposta de sucesso padronizada para a API.
    """
    return Response(
        {
            "success": True,
            "data": data,
        },
        status=status_code,
        headers=headers,
    )


def wrap_success_response(*, response):
    """
    Envolve uma Response do DRF no padrão de sucesso.
    """
    return success_response(
        data=response.data,
        status_code=response.status_code,
        headers=response.headers,
    )
