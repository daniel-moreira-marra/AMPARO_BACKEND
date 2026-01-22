from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


def test_login_by_email_and_me():
    user = User.objects.create_user(
        email="euler@example.com",
        password="strong-password-123",
        full_name="Euler Silva",
        role="CAREGIVER",
    )

    client = APIClient()

    token_resp = client.post(
        "/api/v1/auth/token/",
        {"email": "euler@example.com", "password": "strong-password-123"},
        format="json",
    )
    assert token_resp.status_code == 200
    access = token_resp.json()["data"]["access"]

    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
    me_resp = client.get("/api/v1/auth/me/")
    assert me_resp.status_code == 200
    assert me_resp.json()["data"]["email"] == "euler@example.com"
