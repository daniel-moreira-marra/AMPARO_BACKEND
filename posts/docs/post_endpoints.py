from rest_framework import serializers
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse, extend_schema
from core.docs.schemas import (
    get_success_response_serializer,
    ERROR_400_BAD_REQUEST,
    ERROR_401_UNAUTHORIZED,
    ERROR_403_FORBIDDEN,
    ERROR_404_NOT_FOUND,
    ERROR_409_CONFLICT,
)

from posts.serializers.post_serializers import (
    PostListSerializer,
    PostCreateSerializer,
    PostUpdateSerializer,
    PostLikeResponseSerializer,
)
from posts.serializers.post_comment_serializers import (
    PostCommentCreateSerializer,
    PostCommentListSerializer,
    PostCommentResponseSerializer,
    PostCommentUpdateSerializer,
)

TAG_POSTS = "Posts"


def schema_posts_list():
    return extend_schema(
        tags=[TAG_POSTS],
        summary="Listar minhas postagens",
        description="Retorna apenas postagens do usuário autenticado que não foram deletadas.",
        responses={
            200: get_success_response_serializer(PostListSerializer, many=True),
            401: ERROR_401_UNAUTHORIZED,
        },
    )


def schema_posts_create():
    return extend_schema(
        tags=[TAG_POSTS],
        summary="Criar postagem",
        description="Cria uma nova postagem vinculada ao usuário autenticado.",
        request=PostCreateSerializer,
        responses={
            201: get_success_response_serializer(PostListSerializer),
            400: ERROR_400_BAD_REQUEST,
            401: ERROR_401_UNAUTHORIZED,
        },
        examples=[
            OpenApiExample(
                "Exemplo de Sucesso",
                value={
                    "success": True,
                    "data": {
                        "id": 123,
                        "text": "Minha nova postagem!",
                        "status": "published",
                        "visibility_scope": "public",
                        "created_at": "2024-02-03T14:30:00Z"
                    }
                },
                response_only=True,
                status_codes=["201"],
            )
        ]
    )


def schema_posts_retrieve():
    return extend_schema(
        tags=[TAG_POSTS],
        summary="Detalhar minha postagem",
        responses={
            200: get_success_response_serializer(PostListSerializer),
            401: ERROR_401_UNAUTHORIZED,
            404: ERROR_404_NOT_FOUND,
        },
    )


def schema_posts_update():
    return extend_schema(
        tags=[TAG_POSTS],
        summary="Atualizar minha postagem",
        request=PostUpdateSerializer,
        responses={
            200: get_success_response_serializer(PostListSerializer),
            400: ERROR_400_BAD_REQUEST,
            401: ERROR_401_UNAUTHORIZED,
            403: ERROR_403_FORBIDDEN,
            404: ERROR_404_NOT_FOUND,
        },
    )


def schema_posts_partial_update():
    return extend_schema(
        tags=[TAG_POSTS],
        summary="Atualizar parcialmente minha postagem",
        request=PostUpdateSerializer,
        responses={
            200: get_success_response_serializer(PostListSerializer),
            400: ERROR_400_BAD_REQUEST,
            401: ERROR_401_UNAUTHORIZED,
            403: ERROR_403_FORBIDDEN,
            404: ERROR_404_NOT_FOUND,
        },
    )


def schema_posts_destroy():
    return extend_schema(
        tags=[TAG_POSTS],
        summary="Deletar minha postagem",
        description="Realiza o soft delete de uma postagem do próprio usuário.",
        responses={
            200: get_success_response_serializer(serializers.Serializer),  # Data null
            401: ERROR_401_UNAUTHORIZED,
            403: ERROR_403_FORBIDDEN,
            404: ERROR_404_NOT_FOUND,
        },
    )


def schema_posts_like_create():
    return extend_schema(
        tags=[TAG_POSTS],
        summary="Curtir postagem",
        description="Cria uma curtida do usuário autenticado para o post informado.",
        responses={
            201: get_success_response_serializer(PostLikeResponseSerializer),
            401: ERROR_401_UNAUTHORIZED,
            404: ERROR_404_NOT_FOUND,
            409: ERROR_409_CONFLICT,
        },
        examples=[
            OpenApiExample(
                "Like criado",
                value={
                    "success": True,
                    "data": {
                        "id": 10,
                        "post_id": 15,
                        "user_id": 4,
                        "likes_count": 21,
                        "created_at": "2026-02-21T18:00:00Z",
                    },
                },
                response_only=True,
                status_codes=["201"],
            )
        ],
    )


def schema_posts_unlike_delete():
    return extend_schema(
        tags=[TAG_POSTS],
        summary="Remover curtida de postagem",
        description="Remove a curtida do usuário autenticado no post informado.",
        responses={
            204: OpenApiResponse(description="Curtida removida com sucesso."),
            401: ERROR_401_UNAUTHORIZED,
            404: ERROR_404_NOT_FOUND,
        },
        examples=[
            OpenApiExample(
                "Post não encontrado",
                value={
                    "success": False,
                    "error": {
                        "code": "post_not_found",
                        "message": "Post 999999 not found.",
                        "details": None,
                    },
                },
                response_only=True,
                status_codes=["404"],
            ),
            OpenApiExample(
                "Curtida não encontrada",
                value={
                    "success": False,
                    "error": {
                        "code": "post_like_not_found",
                        "message": "Like for this user and post not found.",
                        "details": None,
                    },
                },
                response_only=True,
                status_codes=["404"],
            ),
        ],
    )


def schema_posts_comment_create():
    return extend_schema(
        tags=[TAG_POSTS],
        summary="Comentar em postagem",
        description="Cria um comentário do usuário autenticado para o post informado.",
        request=PostCommentCreateSerializer,
        responses={
            201: get_success_response_serializer(PostCommentResponseSerializer),
            400: ERROR_400_BAD_REQUEST,
            401: ERROR_401_UNAUTHORIZED,
            404: ERROR_404_NOT_FOUND,
        },
        examples=[
            OpenApiExample(
                "Comentário criado",
                value={
                    "success": True,
                    "data": {
                        "id": 33,
                        "post_id": 15,
                        "user": 4,
                        "user_id": 4,
                        "content": "Ótimo post!",
                        "comments_count": 12,
                        "created_at": "2026-02-22T18:00:00Z",
                        "updated_at": "2026-02-22T18:00:00Z",
                    },
                },
                response_only=True,
                status_codes=["201"],
            ),
            OpenApiExample(
                "Payload inválido",
                value={
                    "content": "   "
                },
                request_only=True,
            ),
        ],
    )


def schema_posts_comment_list():
    return extend_schema(
        tags=[TAG_POSTS],
        summary="Listar comentários de postagem",
        description=(
            "Lista os comentários do post informado.\n\n"
            "**Paginação:**\n"
            "- Usa `CursorPagination` por padrão (parâmetro `cursor`).\n"
            "- Suporta fallback para paginação por página caso o parâmetro `page` seja informado."
        ),
        parameters=[
            OpenApiParameter(
                name="cursor",
                type=OpenApiTypes.STR,
                required=False,
                description="Token do cursor para a próxima página de resultados.",
            ),
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                required=False,
                description="Número da página (ativa modo de paginação tradicional).",
            ),
        ],
        responses={
            200: PostCommentListSerializer(many=True),
            401: ERROR_401_UNAUTHORIZED,
            404: ERROR_404_NOT_FOUND,
        },
        examples=[
            OpenApiExample(
                "Resposta paginada de comentários",
                value={
                    "next": "http://api.exemplo.com/api/v1/posts/comment/15?cursor=cD0yMDI2LTAyLTIy",
                    "previous": None,
                    "results": [
                        {
                            "id": 101,
                            "post_id": 15,
                            "user_id": 4,
                            "content": "Ótimo post!",
                            "created_at": "2026-02-22T18:00:00Z",
                            "updated_at": "2026-02-22T18:00:00Z",
                        }
                    ],
                },
                response_only=True,
                status_codes=["200"],
            )
        ],
    )


def schema_posts_comment_update():
    return extend_schema(
        tags=[TAG_POSTS],
        summary="Editar comentário de postagem",
        description="Atualiza o conteúdo de um comentário existente.",
        request=PostCommentUpdateSerializer,
        responses={
            200: get_success_response_serializer(PostCommentResponseSerializer),
            400: ERROR_400_BAD_REQUEST,
            401: ERROR_401_UNAUTHORIZED,
            403: ERROR_403_FORBIDDEN,
            404: ERROR_404_NOT_FOUND,
        },
        examples=[
            OpenApiExample(
                "Comentário atualizado",
                value={
                    "success": True,
                    "data": {
                        "id": 33,
                        "post_id": 15,
                        "user": 4,
                        "user_id": 4,
                        "content": "Conteúdo atualizado",
                        "comments_count": 12,
                        "created_at": "2026-02-22T18:00:00Z",
                        "updated_at": "2026-02-22T18:30:00Z",
                    },
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Post não encontrado",
                value={
                    "success": False,
                    "error": {
                        "code": "post_not_found",
                        "message": "Post 999999 not found.",
                        "details": None,
                    },
                },
                response_only=True,
                status_codes=["404"],
            ),
            OpenApiExample(
                "Comentário não encontrado no post",
                value={
                    "success": False,
                    "error": {
                        "code": "post_comment_not_found",
                        "message": "Comment 999 for post 15 not found.",
                        "details": None,
                    },
                },
                response_only=True,
                status_codes=["404"],
            ),
            OpenApiExample(
                "Permissão negada",
                value={
                    "success": False,
                    "error": {
                        "code": "comment_permission_denied",
                        "message": "You do not have permission to edit this comment.",
                        "details": None,
                    },
                },
                response_only=True,
                status_codes=["403"],
            ),
        ],
    )


def schema_posts_comment_delete():
    return extend_schema(
        tags=[TAG_POSTS],
        summary="Deletar comentário de postagem",
        description="Remove um comentário existente do post informado.",
        responses={
            204: OpenApiResponse(description="Comentário removido com sucesso."),
            401: ERROR_401_UNAUTHORIZED,
            403: ERROR_403_FORBIDDEN,
            404: ERROR_404_NOT_FOUND,
        },
        examples=[
            OpenApiExample(
                "Post não encontrado",
                value={
                    "success": False,
                    "error": {
                        "code": "post_not_found",
                        "message": "Post 999999 not found.",
                        "details": None,
                    },
                },
                response_only=True,
                status_codes=["404"],
            ),
            OpenApiExample(
                "Comentário não encontrado",
                value={
                    "success": False,
                    "error": {
                        "code": "post_comment_not_found",
                        "message": "Comment 999 for post 15 not found.",
                        "details": None,
                    },
                },
                response_only=True,
                status_codes=["404"],
            ),
            OpenApiExample(
                "Permissão negada",
                value={
                    "success": False,
                    "error": {
                        "code": "comment_permission_denied",
                        "message": "You do not have permission to delete this comment.",
                        "details": None,
                    },
                },
                response_only=True,
                status_codes=["403"],
            ),
        ],
    )
