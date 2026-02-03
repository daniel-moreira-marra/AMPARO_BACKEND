from rest_framework import serializers
from drf_spectacular.utils import OpenApiExample, OpenApiResponse


class ErrorDetailSerializer(serializers.Serializer):
    code = serializers.CharField(help_text="Código de erro único da aplicação.")
    message = serializers.CharField(help_text="Mensagem legível para humanos.")
    details = serializers.JSONField(required=False, allow_null=True, help_text="Detalhes adicionais do erro (ex.: erros de campo).")


class BaseErrorResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=False)
    error = ErrorDetailSerializer()
    request_id = serializers.UUIDField(required=False, help_text="ID da requisição para rastreamento.")


def get_success_response_serializer(data_serializer, many=False):
    """
    Gera dinamicamente um serializer para respostas de sucesso envolvidas.
    Usa o nome do data_serializer para evitar colisões no drf-spectacular.
    """
    serializer_name = data_serializer.__name__.replace("Serializer", "")
    class_name = f"{serializer_name}SuccessResponse"

    class SuccessResponseSerializer(serializers.Serializer):
        success = serializers.BooleanField(default=True)
        data = data_serializer(many=many)

    SuccessResponseSerializer.__name__ = class_name
    return SuccessResponseSerializer


# Respostas comuns de erro para reutilização
ERROR_400_BAD_REQUEST = OpenApiResponse(
    response=BaseErrorResponseSerializer,
    description="Requisição inválida ou erro de validação.",
    examples=[
        OpenApiExample(
            "Erro de Validação",
            value={
                "success": False,
                "error": {
                    "code": "validation_error",
                    "message": "Erro de validação nos dados enviados.",
                    "details": {"text": ["Este campo é obrigatório."]}
                },
                "request_id": "550e8400-e29b-41d5-a716-446655440000"
            }
        )
    ]
)

ERROR_401_UNAUTHORIZED = OpenApiResponse(
    response=BaseErrorResponseSerializer,
    description="Autenticação necessária ou inválida.",
    examples=[
        OpenApiExample(
            "Não Autenticado",
            value={
                "success": False,
                "error": {
                    "code": "not_authenticated",
                    "message": "As credenciais de autenticação não foram fornecidas.",
                    "details": None
                }
            }
        )
    ]
)

ERROR_403_FORBIDDEN = OpenApiResponse(
    response=BaseErrorResponseSerializer,
    description="Permissão negada.",
)

ERROR_404_NOT_FOUND = OpenApiResponse(
    response=BaseErrorResponseSerializer,
    description="Recurso não encontrado.",
)
