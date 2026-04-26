from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from core.docs.schemas import (
    get_success_response_serializer,
    ERROR_401_UNAUTHORIZED,
)

from ..serializers import FeedPostSerializer

TAG_POSTS = "Posts"


def schema_feed_list():
    return extend_schema(
        tags=[TAG_POSTS],
        summary="Listar feed geral",
        description=(
            "Lista postagens publicadas visíveis ao usuário.\n\n"
            "**Regras de Negócio:**\n"
            "- Apenas postagens com status `published` são retornadas.\n"
            "- A visibilidade respeita o escopo configurado pelo autor.\n"
            "- O feed é cacheado por 60 segundos por usuário/página.\n\n"
            "**Paginação:**\n"
            "- Usa `CursorPagination` por padrão (parâmetro `cursor`).\n"
            "- Suporta fallback para paginação por página caso o parâmetro `page` seja informado."
        ),
        parameters=[
            OpenApiParameter(
                name="cursor",
                type=OpenApiTypes.STR,
                required=False,
                description="Token do cursor para a próxima página. Use o campo `next` da resposta anterior.",
            ),
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                required=False,
                description="Número da página (ativa modo de paginação tradicional).",
            ),
            OpenApiParameter(
                name="q",
                type=OpenApiTypes.STR,
                required=False,
                description="Busca textual no conteúdo dos posts.",
            ),
            OpenApiParameter(
                name="role",
                type=OpenApiTypes.STR,
                required=False,
                description=(
                    "Filtrar posts pelo papel do autor. "
                    "Valores: ELDER, CAREGIVER, GUARDIAN, PROFESSIONAL, INSTITUTION."
                ),
                enum=["ELDER", "CAREGIVER", "GUARDIAN", "PROFESSIONAL", "INSTITUTION"],
            ),
            OpenApiParameter(
                name="tag",
                type=OpenApiTypes.STR,
                required=False,
                description="Filtrar posts por tag (busca exata, case-insensitive).",
            ),
        ],
        responses={
            200: get_success_response_serializer(FeedPostSerializer, many=True),
            401: ERROR_401_UNAUTHORIZED,
        },
        examples=[
            OpenApiExample(
                "Resposta do Feed",
                value={
                    "success": True,
                    "data": {
                        "next": "http://api.exemplo.com/api/v1/posts/feed/?cursor=cD0yMDI0LTAyLTAz",
                        "previous": None,
                        "results": [
                            {
                                "id": 1,
                                "author_name": "João Silva",
                                "text": "Olá mundo!",
                                "likes_count": 5,
                                "created_at": "2024-02-03T10:00:00Z"
                            }
                        ]
                    }
                },
                response_only=True,
                status_codes=["200"],
            )
        ]
    )
