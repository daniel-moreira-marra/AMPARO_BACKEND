import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


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
            "phone": "(11) 99999-0000",
            "role": "ELDER",
        },
        format="json",
    )
    assert signup_resp.status_code == 201
    signup_body = signup_resp.json()
    assert signup_body["success"] is True
    assert signup_body["data"]["email"] == "idoso1@example.com"
    assert signup_body["data"]["role"] == "ELDER"
    assert signup_body["data"]["phone"] == "11999990000"

    user = User.objects.get(email="idoso1@example.com")
    assert user.phone == "11999990000"

    # 2) Login por e-mail (ajuste conforme sua rota/serializer de token)
    token_resp = client.post(
        "/api/v1/auth/token/",
        {"email": "idoso1@example.com", "password": "UmaSenhaForte@123"},
        format="json",
    )
    assert token_resp.status_code == 200
    token_body = token_resp.json()
    assert token_body["success"] is True
    access = token_body["data"]["access"]

    # 3) /me
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    me_resp = client.get("/api/v1/auth/me/")
    assert me_resp.status_code == 200
    me_body = me_resp.json()
    assert me_body["success"] is True
    assert me_body["data"]["email"] == "idoso1@example.com"
    assert me_body["data"]["role"] == "ELDER"
