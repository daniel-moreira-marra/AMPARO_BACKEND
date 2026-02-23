import pytest
from accounts.models import InstitutionProfile


@pytest.mark.django_db
def test_institution_me_requires_auth(api_client):
    resp = api_client.get("/api/v1/institutions/me/")
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "NOT_AUTHENTICATED"


@pytest.mark.django_db
def test_institution_me_forbids_non_institution(auth_client):
    client = auth_client(role="ELDER", email="elder_not_inst@example.com")
    resp = client.get("/api/v1/institutions/me/")
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "PERMISSION_DENIED"


@pytest.mark.django_db
def test_institution_me_get_creates_profile(auth_client):
    """
    Criação da instituição: ao acessar GET /institutions/me,
    o profile deve ser criado (get_or_create) e retornado.
    """
    client = auth_client(role="INSTITUTION", email="inst1@example.com")

    assert InstitutionProfile.objects.filter(user__email="inst1@example.com").count() == 0

    resp = client.get("/api/v1/institutions/me/")
    assert resp.status_code == 200

    assert InstitutionProfile.objects.filter(user__email="inst1@example.com").count() == 1

    body = resp.json()["data"]
    # Campos mínimos esperados no response (ajuste conforme seu serializer)
    assert "legal_name" in body


@pytest.mark.django_db
def test_institution_me_patch_updates_fields(auth_client):
    client = auth_client(role="INSTITUTION", email="inst2@example.com")

    # Garante profile existente
    client.get("/api/v1/institutions/me/")

    patch_resp = client.patch(
        "/api/v1/institutions/me/",
        {
            "legal_name": "Casa Serena LTDA",
            "trade_name": "Casa Serena",
            "capacity": 30,
        },
        format="json",
    )
    assert patch_resp.status_code == 200

    body = patch_resp.json()["data"]
    assert body["legal_name"] == "Casa Serena LTDA"
    assert body["trade_name"] == "Casa Serena"
    assert body["capacity"] == 30

    profile = InstitutionProfile.objects.get(user__email="inst2@example.com")
    assert profile.legal_name == "Casa Serena LTDA"
    assert profile.trade_name == "Casa Serena"
    assert profile.capacity == 30


@pytest.mark.django_db
def test_institution_me_rejects_invalid_choice(auth_client):
    """
    Se institution_type for ChoiceField no model/serializer, valores inválidos devem dar 400.
    """
    client = auth_client(role="INSTITUTION", email="inst3@example.com")
    client.get("/api/v1/institutions/me/")

    resp = client.patch(
        "/api/v1/institutions/me/",
        {"institution_type": "NOT_A_REAL_TYPE"},
        format="json",
    )
    assert resp.status_code == 400

    body = resp.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "institution_type" in body["error"]["details"]


@pytest.mark.django_db
def test_institution_me_cannot_change_is_verified(auth_client):
    """
    is_verified deve ser controlado pelo sistema/admin (read_only).
    A API pode ignorar (200) ou rejeitar (400), mas nunca deve alterar o banco.
    """
    client = auth_client(role="INSTITUTION", email="inst_verified@example.com")

    # Garante profile existente
    client.get("/api/v1/institutions/me/")

    profile = InstitutionProfile.objects.get(user__email="inst_verified@example.com")
    original_value = profile.is_verified

    resp = client.patch(
        "/api/v1/institutions/me/",
        {"is_verified": (not original_value)},
        format="json",
    )

    assert resp.status_code in (200, 400), resp.content

    profile.refresh_from_db()
    assert profile.is_verified == original_value
