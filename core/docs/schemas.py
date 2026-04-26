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


# Cache to avoid generating duplicate class objects for the same serializer,
# which would cause drf-spectacular name-collision warnings.
_success_response_cache: dict = {}


def get_success_response_serializer(data_serializer, many=False):
    """
    Gera dinamicamente um serializer para respostas de sucesso envolvidas.
    Usa cache por (serializer, many) para evitar colisões de nomes no drf-spectacular.
    """
    cache_key = (id(data_serializer), many)
    if cache_key in _success_response_cache:
        return _success_response_cache[cache_key]

    serializer_name = data_serializer.__name__.replace("Serializer", "")
    suffix = "ListSuccessResponse" if many else "SuccessResponse"
    class_name = f"{serializer_name}{suffix}"

    class SuccessResponseSerializer(serializers.Serializer):
        success = serializers.BooleanField(default=True)
        data = data_serializer(many=many)

    SuccessResponseSerializer.__name__ = class_name
    SuccessResponseSerializer.__qualname__ = class_name

    _success_response_cache[cache_key] = SuccessResponseSerializer
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

ERROR_409_CONFLICT = OpenApiResponse(
    response=BaseErrorResponseSerializer,
    description="Conflito de estado da requisição.",
)
