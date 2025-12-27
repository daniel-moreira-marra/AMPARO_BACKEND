import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_signup_then_login_then_me():
    client = APIClient()

    # 1) Signup
    signup_resp = client.post(
        "/api/v1/auth/signup/",
        {
            "email": "idoso1@example.com",
            "password": "UmaSenhaForte@123",
            "full_name": "Idoso Exemplo",
            "phone": "11999990000",
            "role": "ELDER",
        },
        format="json",
    )
    assert signup_resp.status_code == 201
    assert signup_resp.json()["email"] == "idoso1@example.com"
    assert signup_resp.json()["role"] == "ELDER"

    # 2) Login por e-mail (ajuste conforme sua rota/serializer de token)
    token_resp = client.post(
        "/api/v1/auth/token/",
        {"email": "idoso1@example.com", "password": "UmaSenhaForte@123"},
        format="json",
    )
    assert token_resp.status_code == 200
    access = token_resp.json()["access"]

    # 3) /me
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    me_resp = client.get("/api/v1/auth/me/")
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "idoso1@example.com"
    assert me_resp.json()["role"] == "ELDER"
