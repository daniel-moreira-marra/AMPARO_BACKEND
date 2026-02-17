import pytest
from django.contrib.auth import get_user_model

from accounts.models import (
    ElderProfile,
    ProfessionalProfile,
)
from links.models import ProfessionalElderLink

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
        "link_type": "professional",
        "elder": elder_profile.id,
        "started_at": "2026-01-20",
        "agreed_hourly_rate": "120.00",
        "service_mode": "HOME",
        "goals": "Reabilitação e ganho de mobilidade.",
        "notes": "Atender 2x por semana.",
    }

    resp = client.post("/api/v1/links/", payload, format="json")
    assert resp.status_code == 201, resp.content

    body = resp.json()
    assert body["status"] == "success"
    data = body["data"]
    assert data["status"] == "PENDING"

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
        "/api/v1/links/",
        {"link_type": "professional", "elder": 999999},
        format="json",
    )

    assert resp.status_code == 400
    body = resp.json()
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

    # Tenta criar novamente via API (deve falhar)
    resp = client.post(
        "/api/v1/links/",
        {
            "link_type": "professional",
            "elder": elder_profile.id,
            "service_mode": "HOME",
        },
        format="json",
    )

    assert resp.status_code == 400
    body = resp.json()
    details = body["error"]["details"]
    assert "elder" in details or "non_field_errors" in details


@pytest.mark.django_db
def test_professional_elder_link_forbidden_for_non_professional(auth_client, create_user):
    """
    Usuário autenticado mas que não é PROFESSIONAL deve receber 400 (Validation Error).
    """
    elder_user = create_user(email="elder_prof_forbidden@example.com", role="ELDER")
    elder_profile = ElderProfile.objects.create(user=elder_user)

    client = auth_client(role="GUARDIAN", email="guardian_not_prof@example.com")

    resp = client.post(
        "/api/v1/links/",
        {"link_type": "professional", "elder": elder_profile.id},
        format="json",
    )

    assert resp.status_code == 400
    assert "non_field_errors" in resp.json()["error"]["details"]

