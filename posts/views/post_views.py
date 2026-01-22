from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from core.exceptions.responses import success_response, wrap_success_response

from ..models import Post
from ..serializers.post_serializers import (
    PostListSerializer,
    PostCreateSerializer,
    PostUpdateSerializer,
)
from ..docs.post_endpoints import (
    schema_posts_list,
    schema_posts_create,
    schema_posts_retrieve,
    schema_posts_update,
    schema_posts_partial_update,
    schema_posts_destroy,
)


class IsAuthenticated(permissions.IsAuthenticated):
    """Alias explícito para legibilidade."""
    pass


class MyPostsViewSet(viewsets.ModelViewSet):
    """
    CRUD de postagens do próprio usuário.
    - Queryset sempre filtrado por author=request.user
    - Exclui soft-deletadas (deleted_at)
    """

    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post", "put", "patch", "delete"]

    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_queryset(self):
        qs = Post.objects.filter(author=self.request.user)

        # Soft delete (se o campo existir no seu model)
        if hasattr(Post, "deleted_at"):
            qs = qs.filter(deleted_at__isnull=True)

        # Ordenação de feed pessoal
        return qs.order_by("-created_at")

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "create":
            return PostCreateSerializer
        if self.action in ("update", "partial_update"):
            return PostUpdateSerializer
        return PostListSerializer

    @schema_posts_list()
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return wrap_success_response(response=response)

    @schema_posts_create()
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        post = serializer.save()

        # Resposta no formato do "list/retrieve"
        response = Response(PostListSerializer(post).data, status=status.HTTP_201_CREATED)
        return wrap_success_response(response=response)

    @schema_posts_retrieve()
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return wrap_success_response(response=response)

    @schema_posts_update()
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return wrap_success_response(response=response)

    @schema_posts_partial_update()
    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        return wrap_success_response(response=response)

    @schema_posts_destroy()
    def destroy(self, request, *args, **kwargs):
        post = self.get_object()

        # Soft delete (preferível)
        if hasattr(post, "deleted_at"):
            post.deleted_at = timezone.now()
            post.save(update_fields=["deleted_at"])
            return success_response(data=None, status_code=status.HTTP_200_OK)

        # Fallback: hard delete
        post.delete()
        return success_response(data=None, status_code=status.HTTP_200_OK)
