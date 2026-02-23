import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
def test_signup_institution_requires_address():
    client = APIClient()
    resp = client.post(
        "/api/v1/auth/signup/",
        {
            "email": "inst_no_address@example.com",
            "password": "UmaSenhaForte@123",
            "full_name": "Instituicao Sem Endereco",
            "role": "INSTITUTION",
        },
        format="json",
    )
    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "address_line" in body["error"]["details"]


@pytest.mark.django_db
def test_signup_institution_persists_address():
    client = APIClient()
    resp = client.post(
        "/api/v1/auth/signup/",
        {
            "email": "inst_with_address@example.com",
            "password": "UmaSenhaForte@123",
            "full_name": "Instituicao Com Endereco",
            "role": "INSTITUTION",
            "address_line": "Rua das Flores, 123",
            "city": "São Paulo",
            "state": "SP",
            "zip_code": "01001000",
        },
        format="json",
    )
    assert resp.status_code == 201
    user = User.objects.get(email="inst_with_address@example.com")
    assert user.address_line == "Rua das Flores, 123"
    assert user.city == "São Paulo"
    assert user.state == "SP"
    assert user.zip_code == "01001000"


@pytest.mark.django_db
def test_signup_institution_sanitizes_zip_code_and_normalizes_state():
    client = APIClient()
    resp = client.post(
        "/api/v1/auth/signup/",
        {
            "email": "inst_sanitize@example.com",
            "password": "UmaSenhaForte@123",
            "full_name": "Instituicao Sanitize",
            "role": "INSTITUTION",
            "address_line": "Rua das Flores, 123",
            "city": "São Paulo",
            "state": " sp ",
            "zip_code": "01001-000",
        },
        format="json",
    )
    assert resp.status_code == 201
    user = User.objects.get(email="inst_sanitize@example.com")
    assert user.state == "SP"
    assert user.zip_code == "01001000"


@pytest.mark.django_db
def test_signup_rejects_invalid_state():
    client = APIClient()
    resp = client.post(
        "/api/v1/auth/signup/",
        {
            "email": "invalid_state@example.com",
            "password": "UmaSenhaForte@123",
            "full_name": "Usuario Invalido",
            "role": "ELDER",
            "state": "XX",
        },
        format="json",
    )
    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "invalid_state"
    assert "state" in body["error"]["details"]


@pytest.mark.django_db
def test_me_patch_updates_address(auth_client):
    client = auth_client(email="user_addr@example.com", role="ELDER")
    resp = client.patch(
        "/api/v1/auth/me/",
        {
            "address_line": "Av. Central, 456",
            "city": "Campinas",
            "state": "SP",
            "zip_code": "13010000",
        },
        format="json",
    )
    assert resp.status_code == 200
    body = resp.json()["data"]
    assert body["address_line"] == "Av. Central, 456"
    assert body["city"] == "Campinas"
    assert body["state"] == "SP"
    assert body["zip_code"] == "13010000"


@pytest.mark.django_db
def test_me_patch_sanitizes_phone_and_zip_code(auth_client):
    client = auth_client(email="user_phone_zip@example.com", role="ELDER")
    resp = client.patch(
        "/api/v1/auth/me/",
        {
            "phone": "(11) 98888-7777",
            "zip_code": "01001-000",
        },
        format="json",
    )
    assert resp.status_code == 200
    body = resp.json()["data"]
    assert body["phone"] == "11988887777"
    assert body["zip_code"] == "01001000"


@pytest.mark.django_db
def test_me_patch_normalizes_state(auth_client):
    client = auth_client(email="user_state_norm@example.com", role="ELDER")
    resp = client.patch(
        "/api/v1/auth/me/",
        {"state": " rj "},
        format="json",
    )
    assert resp.status_code == 200
    body = resp.json()["data"]
    assert body["state"] == "RJ"


@pytest.mark.django_db
def test_me_patch_rejects_invalid_state(auth_client):
    client = auth_client(email="user_state_invalid@example.com", role="ELDER")
    resp = client.patch(
        "/api/v1/auth/me/",
        {"state": "XX"},
        format="json",
    )
    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "invalid_state"
    assert "state" in body["error"]["details"]
