from drf_spectacular.utils import (
    OpenApiResponse,
    extend_schema,
)

from posts.serializers.post_serializers import (
    PostListSerializer,
    PostCreateSerializer,
    PostUpdateSerializer,
)


def schema_posts_list():
    return extend_schema(
        tags=["Posts"],
        summary="Listar minhas postagens",
        description="Retorna apenas postagens do usuário autenticado (não deletadas).",
        responses={200: PostListSerializer(many=True)},
    )


def schema_posts_create():
    return extend_schema(
        tags=["Posts"],
        summary="Criar postagem",
        description="Cria uma postagem vinculada ao usuário autenticado.",
        request=PostCreateSerializer,
        responses={201: PostListSerializer},
)


def schema_posts_retrieve():
    return extend_schema(
        tags=["Posts"],
        summary="Detalhar minha postagem",
        responses={200: PostListSerializer},
    )


def schema_posts_update():
    return extend_schema(
        tags=["Posts"],
        summary="Atualizar minha postagem",
        request=PostUpdateSerializer,
        responses={200: PostListSerializer},
    )


def schema_posts_partial_update():
    return extend_schema(
        tags=["Posts"],
        summary="Atualizar parcialmente minha postagem",
        request=PostUpdateSerializer,
        responses={200: PostListSerializer},
    )


def schema_posts_destroy():
    return extend_schema(
        tags=["Posts"],
        summary="Deletar minha postagem",
        description="Deleta (soft delete, se existir deleted_at) apenas uma postagem do próprio usuário.",
        responses={
            204: OpenApiResponse(description="Postagem deletada com sucesso."),
        },
    )
