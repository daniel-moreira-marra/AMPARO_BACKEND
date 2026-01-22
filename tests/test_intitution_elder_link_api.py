import pytest
from django.contrib.auth import get_user_model

from accounts.models import (
    ElderProfile,
    InstitutionProfile,
    InstitutionElderLink,
)

User = get_user_model()


@pytest.mark.django_db
def test_institution_elder_link_create_success(auth_client, create_user):
    """
    Deve permitir que uma INSTITUTION crie vínculo com um ELDER existente.
    """
    # cria elder + profile
    elder_user = create_user(email="elder_inst_ok@example.com", role="ELDER")
    elder_profile = ElderProfile.objects.create(user=elder_user)

    # autentica instituição
    client = auth_client(role="INSTITUTION", email="inst_link_ok@example.com")
    inst_user = User.objects.get(email="inst_link_ok@example.com")
    inst_profile, _ = InstitutionProfile.objects.get_or_create(user=inst_user)

    payload = {
        "elder": elder_profile.id,
        "status": "ACTIVE",
        "admitted_at": "2026-01-10",
        "room": "12",
        "bed": "B",
        "notes": "Chegou por encaminhamento.",
        "is_active": True,
    }

    resp = client.post("/api/v1/institutions/me/link-to-elder/", payload, format="json")
    assert resp.status_code == 201, resp.content

    body = resp.json()["data"]
    assert body["institution"] == inst_profile.id
    assert body["elder"] == elder_profile.id
    assert body["status"] == "ACTIVE"
    assert body["is_active"] is True

    assert InstitutionElderLink.objects.filter(
        institution=inst_profile,
        elder=elder_profile,
        is_active=True,
    ).exists()


@pytest.mark.django_db
def test_institution_elder_link_create_fails_when_elder_not_found(auth_client):
    """
    Deve retornar 400 ao tentar criar vínculo com elder inexistente.
    """
    client = auth_client(role="INSTITUTION", email="inst_elder_nf@example.com")
    inst_user = User.objects.get(email="inst_elder_nf@example.com")
    InstitutionProfile.objects.get_or_create(user=inst_user)

    resp = client.post(
        "/api/v1/institutions/me/link-to-elder/",
        {"elder": 999999, "status": "ACTIVE", "is_active": True},
        format="json",
    )

    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "elder" in body["error"]["details"]


@pytest.mark.django_db
def test_institution_elder_link_create_fails_when_duplicate_active_link(auth_client, create_user):
    """
    Deve retornar 400 ao tentar criar vínculo ativo duplicado (mesma institution + mesmo elder).
    """
    elder_user = create_user(email="elder_inst_dup@example.com", role="ELDER")
    elder_profile = ElderProfile.objects.create(user=elder_user)

    client = auth_client(role="INSTITUTION", email="inst_dup@example.com")
    inst_user = User.objects.get(email="inst_dup@example.com")
    inst_profile, _ = InstitutionProfile.objects.get_or_create(user=inst_user)

    # cria vínculo ativo existente no banco
    InstitutionElderLink.objects.create(
        institution=inst_profile,
        elder=elder_profile,
        status=InstitutionElderLink.Status.ACTIVE,
        is_active=True,
        room="10",
        bed="A",
    )

    # tenta criar novamente via API
    resp = client.post(
        "/api/v1/institutions/me/link-to-elder/",
        {"elder": elder_profile.id, "status": "ACTIVE", "is_active": True},
        format="json",
    )

    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    # pode cair em "elder" (validate) ou em "non_field_errors" (constraint)
    assert ("elder" in body["error"]["details"]) or ("non_field_errors" in body["error"]["details"])


@pytest.mark.django_db
def test_institution_elder_link_forbidden_for_non_institution(auth_client, create_user):
    """
    Usuário autenticado mas que não é INSTITUTION deve receber 403.
    """
    elder_user = create_user(email="elder_inst_forbidden@example.com", role="ELDER")
    elder_profile = ElderProfile.objects.create(user=elder_user)

    # autentica como CAREGIVER (ou ELDER)
    client = auth_client(role="CAREGIVER", email="cg_not_inst@example.com")

    resp = client.post(
        "/api/v1/institutions/me/link-to-elder/",
        {"elder": elder_profile.id, "status": "ACTIVE", "is_active": True},
        format="json",
    )

    assert resp.status_code == 403
    body = resp.json()
    assert body["error"]["code"] == "PERMISSION_DENIED"
