from rest_framework import serializers
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from core.docs.schemas import (
    get_success_response_serializer,
    ERROR_400_BAD_REQUEST,
    ERROR_401_UNAUTHORIZED,
    ERROR_403_FORBIDDEN,
    ERROR_404_NOT_FOUND,
)

from posts.serializers.post_serializers import (
    PostListSerializer,
    PostCreateSerializer,
    PostUpdateSerializer,
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


def schema_posts_like():
    """
    Template para o endpoint de Like (caso seja implementado).
    """
    return extend_schema(
        tags=[TAG_POSTS],
        summary="Curtir/Descurtir postagem",
        description="Alterna o estado de 'curtida' do usuário na postagem.",
        responses={
            200: OpenApiResponse(
                description="Status da curtida atualizado.",
                examples=[
                    OpenApiExample("Sucesso", value={"success": True, "data": {"liked": True, "likes_count": 10}})
                ]
            ),
            401: ERROR_401_UNAUTHORIZED,
            404: ERROR_404_NOT_FOUND,
        },
    )
