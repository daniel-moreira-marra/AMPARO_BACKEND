from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from ..serializers import FeedPostSerializer


def schema_feed_list():
    return extend_schema(
        tags=["Posts"],
        summary="Listar feed geral",
        description=(
            "Lista postagens publicadas visíveis ao usuário.\n\n"
            "- Usa CursorPagination por padrão\n"
            "- Se o parâmetro `page` for informado, usa paginação por página (fallback)"
        ),
        parameters=[
            OpenApiParameter(
                name="cursor",
                type=OpenApiTypes.STR,
                required=False,
                description="Cursor da paginação (usado no modo cursor).",
            ),
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                required=False,
                description="Ativa fallback por página (se informado).",
            ),
        ],
        responses={200: FeedPostSerializer(many=True)},
    )
