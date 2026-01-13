from rest_framework.response import Response


def error_response(*, code: str, message: str, status_code: int, details=None):
    """
    Gera uma resposta de erro padronizada para a API.
    """
    return Response(
        {
            "error": {
                "code": code,
                "message": message,
                "details": details,
            }
        },
        status=status_code,
    )
