from django.utils import timezone
from rest_framework import permissions, status, viewsets
from ..permissions import IsPostOwner, CanEditPost, CanViewPost
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
from ..services.post_services import create_post, delete_post


class IsAuthenticated(permissions.IsAuthenticated):
    """Alias explícito para legibilidade."""
    pass


class MyPostsViewSet(viewsets.ModelViewSet):
    """
    CRUD de postagens do próprio usuário.
    - Queryset sempre filtrado por author=request.user
    - Exclui soft-deletadas (deleted_at)
    """

    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """
        Garante que para ações de escrita (update/destroy), somente o dono possa agir.
        Isso complementa o filtro do get_queryset.
        """
        if self.action in ["update", "partial_update", "destroy"]:
            return [permissions.IsAuthenticated(), CanEditPost()]
        if self.action == "retrieve":
            return [permissions.IsAuthenticated(), CanViewPost()]
        return super().get_permissions()
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

        images = request.FILES.getlist("images")

        # Use Service Layer
        post = create_post(
            actor=request.user,
            data=serializer.validated_data,
            images=images or None,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT"),
        )

        response = Response(PostListSerializer(post).data, status=status.HTTP_201_CREATED)
        return wrap_success_response(response=response)

    @schema_posts_retrieve()
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return wrap_success_response(response=response)

    @schema_posts_update()
    def update(self, request, *args, **kwargs):
        super().update(request, *args, **kwargs)
        post = self.get_object()
        return success_response(data=PostListSerializer(post).data)

    @schema_posts_partial_update()
    def partial_update(self, request, *args, **kwargs):
        super().partial_update(request, *args, **kwargs)
        post = self.get_object()
        return success_response(data=PostListSerializer(post).data)

    @schema_posts_destroy()
    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        
        # Use Service Layer
        delete_post(actor=request.user, post_id=post.id)
        
        return success_response(data=None, status_code=status.HTTP_200_OK)
