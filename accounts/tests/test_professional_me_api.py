import pytest
from accounts.models import ProfessionalProfile


@pytest.mark.django_db
def test_professional_me_requires_auth(api_client):
    resp = api_client.get("/api/v1/professionals/me/")
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "NOT_AUTHENTICATED"


@pytest.mark.django_db
def test_professional_me_forbids_non_professional(auth_client):
    client = auth_client(role="ELDER", email="elder_not_prof@example.com")
    resp = client.get("/api/v1/professionals/me/")
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "PERMISSION_DENIED"


@pytest.mark.django_db
def test_professional_me_get_creates_profile(auth_client):
    """
    Criação do profissional: ao acessar GET /professionals/me,
    o profile deve ser criado (get_or_create) e retornado.
    """
    client = auth_client(role="PROFESSIONAL", email="prof1@example.com")

    assert ProfessionalProfile.objects.filter(user__email="prof1@example.com").count() == 0

    resp = client.get("/api/v1/professionals/me/")
    assert resp.status_code == 200

    assert ProfessionalProfile.objects.filter(user__email="prof1@example.com").count() == 1

    body = resp.json()
    # Campos mínimos esperados no response (ajuste conforme seu serializer)
    assert "profession" in body
    assert "city" in body
    assert "state" in body


@pytest.mark.django_db
def test_professional_me_patch_updates_fields(auth_client):
    client = auth_client(role="PROFESSIONAL", email="prof2@example.com")

    # Garante profile existente
    client.get("/api/v1/professionals/me/")

    patch_resp = client.patch(
        "/api/v1/professionals/me/",
        {
            "bio": "Fisioterapeuta com foco em reabilitação.",
            "city": "São Paulo",
            "state": "SP",
            "is_available": True,
        },
        format="json",
    )
    assert patch_resp.status_code == 200
    body = patch_resp.json()
    assert body["bio"] == "Fisioterapeuta com foco em reabilitação."
    assert body["city"] == "São Paulo"
    assert body["state"] == "SP"
    assert body["is_available"] is True

    profile = ProfessionalProfile.objects.get(user__email="prof2@example.com")
    assert profile.bio == "Fisioterapeuta com foco em reabilitação."
    assert profile.city == "São Paulo"
    assert profile.state == "SP"
    assert profile.is_available is True


@pytest.mark.django_db
def test_professional_me_rejects_invalid_choice(auth_client):
    """
    Se profession for ChoiceField no model/serializer, valores inválidos devem dar 400.
    """
    client = auth_client(role="PROFESSIONAL", email="prof3@example.com")
    client.get("/api/v1/professionals/me/")

    resp = client.patch(
        "/api/v1/professionals/me/",
        {"profession": "NOT_A_REAL_PROFESSION"},
        format="json",
    )
    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "profession" in body["error"]["details"]

@pytest.mark.django_db
def test_professional_me_cannot_change_registration_verified(auth_client):
    client = auth_client(role="PROFESSIONAL", email="prof_verified@example.com")

    # Garante profile existente
    client.get("/api/v1/professionals/me/")
    profile = ProfessionalProfile.objects.get(user__email="prof_verified@example.com")
    original_value = profile.registration_verified

    # Tenta alterar via PATCH (mais confiável que PUT)
    resp = client.patch(
        "/api/v1/professionals/me/",
        {"registration_verified": (not original_value)},
        format="json",
    )

    # Pode ser 200 (campo ignorado) ou 400 (request rejeitado por regra/serializer)
    assert resp.status_code in (200, 400), resp.content

    profile.refresh_from_db()
    assert profile.registration_verified == original_value
