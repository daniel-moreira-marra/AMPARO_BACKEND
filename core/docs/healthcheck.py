"""
Documentação Swagger/OpenAPI para o Health Check.

Requer: drf-spectacular
- pip install drf-spectacular
- Configure o DEFAULT_SCHEMA_CLASS no settings.py.
"""

from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status


def healthcheck_docs():
    """
    Retorna o decorator `extend_schema` pronto para ser aplicado na view.

    Uso:
        @healthcheck_docs()
        def get(...):
            ...
    """
    return extend_schema(
        tags=["Health"],
        summary="Health check da API",
        description=(
            "Endpoint público para o frontend (ou monitoramento) verificar se a API está ativa. "
            "Não exige autenticação."
        ),
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                description="API ativa",
                response={
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean", "example": True},
                        "data": {
                            "type": "object",
                            "properties": {
                                "status": {"type": "string", "example": "ok"},
                                "message": {
                                    "type": "string",
                                    "example": "API de rede de cuidados ativa",
                                },
                            },
                            "required": ["status", "message"],
                        },
                    },
                    "required": ["success", "data"],
                },
            )
        },
    )

