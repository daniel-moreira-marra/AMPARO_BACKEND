import pytest
from django.contrib.auth import get_user_model

from accounts.models import (
    ElderProfile,
    CaregiverProfile,
    CaregiverElderLink,
)

User = get_user_model()


@pytest.mark.django_db
def test_caregiver_link_to_elder_create_success(auth_client, create_user):
    """
    Deve permitir que um CAREGIVER crie vínculo com um ELDER existente.
    """
    elder_user = create_user(email="elder_cg_ok@example.com", role="ELDER")
    elder_profile = ElderProfile.objects.create(user=elder_user)

    client = auth_client(role="CAREGIVER", email="cg_link_ok@example.com")
    cg_user = User.objects.get(email="cg_link_ok@example.com")
    caregiver_profile, _ = CaregiverProfile.objects.get_or_create(user=cg_user)

    payload = {
        "elder": elder_profile.id,
        "status": "PENDING",
        "started_at": "2026-01-20",
        "agreed_hourly_rate": "80.00",
        "notes": "Atendimento 3x por semana.",
        "is_active": True,
    }

    resp = client.post("/api/v1/caregivers/me/link-to-elder/", payload, format="json")
    assert resp.status_code == 201, resp.content

    body = resp.json()["data"]
    assert body["caregiver"] == caregiver_profile.id
    assert body["elder"] == elder_profile.id
    assert body["status"] == "PENDING"
    assert body["is_active"] is True

    assert CaregiverElderLink.objects.filter(
        caregiver=caregiver_profile,
        elder=elder_profile,
        is_active=True,
    ).exists()


@pytest.mark.django_db
def test_caregiver_link_to_elder_create_fails_when_elder_not_found(auth_client):
    """
    Deve retornar 400 ao tentar criar vínculo com elder inexistente.
    """
    client = auth_client(role="CAREGIVER", email="cg_elder_nf@example.com")
    cg_user = User.objects.get(email="cg_elder_nf@example.com")
    CaregiverProfile.objects.get_or_create(user=cg_user)

    resp = client.post(
        "/api/v1/caregivers/me/link-to-elder/",
        {"elder": 999999, "status": "PENDING", "is_active": True},
        format="json",
    )

    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "elder" in body["error"]["details"]


@pytest.mark.django_db
def test_caregiver_link_to_elder_create_fails_when_duplicate_active_link(auth_client, create_user):
    """
    Deve retornar 400 ao tentar criar vínculo ativo duplicado (mesmo caregiver + mesmo elder).
    """
    elder_user = create_user(email="elder_cg_dup@example.com", role="ELDER")
    elder_profile = ElderProfile.objects.create(user=elder_user)

    client = auth_client(role="CAREGIVER", email="cg_dup@example.com")
    cg_user = User.objects.get(email="cg_dup@example.com")
    caregiver_profile, _ = CaregiverProfile.objects.get_or_create(user=cg_user)

    CaregiverElderLink.objects.create(
        caregiver=caregiver_profile,
        elder=elder_profile,
        status=CaregiverElderLink.Status.ACTIVE,
        is_active=True,
        notes="Vínculo existente",
    )

    resp = client.post(
        "/api/v1/caregivers/me/link-to-elder/",
        {"elder": elder_profile.id, "status": "PENDING", "is_active": True},
        format="json",
    )

    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    # pode cair no validate() (elder) ou no constraint (non_field_errors)
    assert ("elder" in body["error"]["details"]) or ("non_field_errors" in body["error"]["details"])


@pytest.mark.django_db
def test_caregiver_link_to_elder_forbidden_for_non_caregiver(auth_client, create_user):
    """
    Usuário autenticado mas que não é CAREGIVER deve receber 403.
    """
    elder_user = create_user(email="elder_cg_forbidden@example.com", role="ELDER")
    elder_profile = ElderProfile.objects.create(user=elder_user)

    client = auth_client(role="GUARDIAN", email="guardian_not_cg@example.com")

    resp = client.post(
        "/api/v1/caregivers/me/link-to-elder/",
        {"elder": elder_profile.id, "status": "PENDING", "is_active": True},
        format="json",
    )

    assert resp.status_code == 403
    body = resp.json()
    assert body["error"]["code"] == "PERMISSION_DENIED"
