import pytest
from django.contrib.auth import get_user_model

from accounts.models import (
    ElderProfile,
    ProfessionalProfile,
    ProfessionalElderLink,
)

User = get_user_model()


@pytest.mark.django_db
def test_professional_elder_link_create_success(auth_client, create_user):
    """
    Deve permitir que um PROFESSIONAL crie vínculo com um ELDER existente.
    """
    elder_user = create_user(email="elder_prof_ok@example.com", role="ELDER")
    elder_profile = ElderProfile.objects.create(user=elder_user)

    client = auth_client(role="PROFESSIONAL", email="prof_link_ok@example.com")
    prof_user = User.objects.get(email="prof_link_ok@example.com")
    prof_profile, _ = ProfessionalProfile.objects.get_or_create(user=prof_user)

    payload = {
        "elder": elder_profile.id,
        "status": "PENDING",
        "started_at": "2026-01-20",
        "agreed_hourly_rate": "120.00",
        "service_mode": "HOME",
        "goals": "Reabilitação e ganho de mobilidade.",
        "notes": "Atender 2x por semana.",
        "is_active": True,
    }

    resp = client.post("/api/v1/professionals/me/link-to-elder/", payload, format="json")
    assert resp.status_code == 201, resp.content

    body = resp.json()["data"]
    assert body["professional"] == prof_profile.id
    assert body["elder"] == elder_profile.id
    assert body["status"] == "PENDING"
    assert body["is_active"] is True

    assert ProfessionalElderLink.objects.filter(
        professional=prof_profile,
        elder=elder_profile,
        is_active=True,
    ).exists()


@pytest.mark.django_db
def test_professional_elder_link_create_fails_when_elder_not_found(auth_client):
    """
    Deve retornar 400 ao tentar criar vínculo com elder inexistente.
    """
    client = auth_client(role="PROFESSIONAL", email="prof_elder_nf@example.com")
    prof_user = User.objects.get(email="prof_elder_nf@example.com")
    ProfessionalProfile.objects.get_or_create(user=prof_user)

    resp = client.post(
        "/api/v1/professionals/me/link-to-elder/",
        {
            "elder": 999999,
            "status": "PENDING",
            "is_active": True,
        },
        format="json",
    )

    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "elder" in body["error"]["details"]


@pytest.mark.django_db
def test_professional_elder_link_create_fails_when_duplicate_active_link(auth_client, create_user):
    """
    Deve retornar 400 ao tentar criar vínculo ativo duplicado (mesmo professional + mesmo elder).
    """
    elder_user = create_user(email="elder_prof_dup@example.com", role="ELDER")
    elder_profile = ElderProfile.objects.create(user=elder_user)

    client = auth_client(role="PROFESSIONAL", email="prof_dup@example.com")
    prof_user = User.objects.get(email="prof_dup@example.com")
    prof_profile, _ = ProfessionalProfile.objects.get_or_create(user=prof_user)

    ProfessionalElderLink.objects.create(
        professional=prof_profile,
        elder=elder_profile,
        status=ProfessionalElderLink.Status.ACTIVE,
        is_active=True,
        service_mode="HOME",
    )

    resp = client.post(
        "/api/v1/professionals/me/link-to-elder/",
        {"elder": elder_profile.id, "status": "PENDING", "is_active": True},
        format="json",
    )

    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    # pode cair no validate() (elder) ou no constraint (non_field_errors)
    assert ("elder" in body["error"]["details"]) or ("non_field_errors" in body["error"]["details"])


@pytest.mark.django_db
def test_professional_elder_link_forbidden_for_non_professional(auth_client, create_user):
    """
    Usuário autenticado mas que não é PROFESSIONAL deve receber 403.
    """
    elder_user = create_user(email="elder_prof_forbidden@example.com", role="ELDER")
    elder_profile = ElderProfile.objects.create(user=elder_user)

    client = auth_client(role="GUARDIAN", email="guardian_not_prof@example.com")

    resp = client.post(
        "/api/v1/professionals/me/link-to-elder/",
        {"elder": elder_profile.id, "status": "PENDING", "is_active": True},
        format="json",
    )

    assert resp.status_code == 403
    body = resp.json()
    assert body["error"]["code"] == "PERMISSION_DENIED"
