import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

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
        access = token_resp.json()["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        return api_client

    return _auth
