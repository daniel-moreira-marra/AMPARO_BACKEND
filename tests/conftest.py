import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from django.utils import timezone
from posts.models import Post
from posts.enums import PostStatus
from posts.enums import VisibilityScope

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user(db):
    """
    Factory simples para criar usuários.
    """
    def _create_user(**kwargs):
        password = kwargs.pop("password", "StrongPass@123")
        email = kwargs.pop("email", "user@example.com")
        full_name = kwargs.pop("full_name", "User Test")
        role = kwargs.pop("role", "ELDER")

        return User.objects.create_user(
            email=email,
            password=password,
            full_name=full_name,
            role=role,
            **kwargs,
        )
    return _create_user


@pytest.fixture
def auth_client(api_client, create_user):
    """
    Retorna um client autenticado via JWT.
    """
    def _auth(role="ELDER", email="elder@example.com", password="StrongPass@123"):
        create_user(email=email, password=password, role=role)
        token_resp = api_client.post(
            "/api/v1/auth/token/",
            {"email": email, "password": password},
            format="json",
        )
        assert token_resp.status_code == 200, token_resp.content
        access = token_resp.json()["data"]["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        return api_client

    return _auth


@pytest.fixture
def create_post(create_user):
    """
    Factory para criar Post diretamente no banco.
    Útil para cenários de listagem/edição sem depender do endpoint de criação.
    """
    def _create_post(*, author=None, text="Olá", status=None, visibility_scope=None, **kwargs):
        author = author or create_user(email="author@example.com")
        status = status or PostStatus.DRAFT
        visibility_scope = visibility_scope or VisibilityScope.PUBLIC

        post = Post.objects.create(
            author=author,
            author_role=getattr(author, "role", "") or "",
            text=text,
            status=status,
            visibility_scope=visibility_scope,
            **kwargs,
        )

        # Se seu model usa published_at, simula coerência quando publicado
        if hasattr(post, "published_at") and status == PostStatus.PUBLISHED and not post.published_at:
            post.published_at = timezone.now()
            post.save(update_fields=["published_at"])

        return post

    return _create_post
