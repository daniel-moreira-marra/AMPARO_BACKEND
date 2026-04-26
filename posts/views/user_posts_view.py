from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from core.exceptions.responses import success_response
from core.docs.schemas import (
    get_success_response_serializer,
    ERROR_401_UNAUTHORIZED,
    ERROR_404_NOT_FOUND,
)
from ..models import Post, PostLike
from ..serializers.feed_serializers import FeedPostSerializer

User = get_user_model()


class UserPostsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Posts"],
        summary="Posts publicados de um usuário",
        description=(
            "Retorna os últimos 20 posts publicados de um usuário específico, "
            "ordenados do mais recente para o mais antigo.\n\n"
            "**Uso:** exibir os posts no perfil público de outro usuário.\n\n"
            "**Inclui:** informações de curtida (`liked_by_me`) relativas ao usuário autenticado."
        ),
        parameters=[
            OpenApiParameter(
                name="pk",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="ID do usuário cujos posts serão listados.",
                required=True,
            ),
        ],
        responses={
            200: get_success_response_serializer(FeedPostSerializer, many=True),
            401: ERROR_401_UNAUTHORIZED,
            404: ERROR_404_NOT_FOUND,
        },
        examples=[
            OpenApiExample(
                "Lista de posts do usuário",
                value={
                    "success": True,
                    "data": [
                        {
                            "id": 15,
                            "author_id": 7,
                            "author_name": "Carlos Andrade",
                            "author_avatar": "https://storage.exemplo.com/avatars/7.jpg",
                            "author_role": "CAREGIVER",
                            "text": "Dicas para estimulação cognitiva em idosos com demência leve.",
                            "image": None,
                            "image_alt_text": None,
                            "images": [],
                            "tags": ["demência", "estimulação"],
                            "likes_count": 12,
                            "comments_count": 3,
                            "liked_by_me": True,
                            "shared_post": None,
                            "created_at": "2026-04-15T10:00:00Z",
                            "published_at": "2026-04-15T10:00:00Z",
                        }
                    ],
                },
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def get(self, request, pk):
        user = get_object_or_404(User, id=pk, is_active=True)
        posts = (
            Post.objects.filter(
                author=user,
                deleted_at__isnull=True,
                status="PUBLISHED",
            )
            .select_related("author", "parent_post", "parent_post__author")
            .prefetch_related("post_images", "parent_post__post_images")
            .annotate(
                _liked_by_me=Exists(
                    PostLike.objects.filter(post=OuterRef("pk"), user=request.user)
                )
            )
            .order_by("-created_at")[:20]
        )

        data = FeedPostSerializer(posts, many=True, context={"request": request}).data
        return success_response(data=list(data))
