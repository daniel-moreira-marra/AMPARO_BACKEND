import pytest
from django.contrib.auth import get_user_model

from accounts.models import ElderProfile, GuardianProfile, GuardianElderLink

User = get_user_model()
route_under_test = "/api/v1/guardians/link-to-elder/"

@pytest.mark.django_db
def test_guardian_elder_link_create_success(auth_client, create_user):
    """
    Deve permitir que um GUARDIAN crie vínculo com um ELDER existente.
    """
    # Cria elder + profile
    elder_user = create_user(email="elder_link_ok@example.com", role="ELDER")
    elder_profile = ElderProfile.objects.create(user=elder_user)

    # Autentica guardian
    client = auth_client(role="GUARDIAN", email="guardian_link_ok@example.com")
    guardian_user = User.objects.get(email="guardian_link_ok@example.com")
    guardian_profile, _ = GuardianProfile.objects.get_or_create(user=guardian_user)

    payload = {
        "elder": elder_profile.id,
        "relationship": "CHILD",
        "is_legal_guardian": True,
        "can_view_medical": True,
        "can_hire": True,
        "is_active": True,
    }

    resp = client.post(route_under_test, payload, format="json")
    assert resp.status_code == 201, resp.content

    body = resp.json()
    assert body["guardian"] == guardian_profile.id
    assert body["elder"] == elder_profile.id
    assert body["relationship"] == "CHILD"
    assert body["is_active"] is True

    assert GuardianElderLink.objects.filter(
        guardian=guardian_profile,
        elder=elder_profile,
        is_active=True,
    ).exists()


@pytest.mark.django_db
def test_guardian_elder_link_create_fails_when_elder_not_found(auth_client):
    """
    Deve retornar 400 ao tentar criar vínculo com elder inexistente.
    """
    client = auth_client(role="GUARDIAN", email="guardian_elder_nf@example.com")
    guardian_user = User.objects.get(email="guardian_elder_nf@example.com")
    GuardianProfile.objects.get_or_create(user=guardian_user)

    resp = client.post(
        route_under_test,
        {
            "elder": 999999,  # id inexistente
            "relationship": "CHILD",
            "is_active": True,
        },
        format="json",
    )

    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "elder" in body["error"]["details"]


@pytest.mark.django_db
def test_guardian_elder_link_create_fails_when_duplicate_active_link(auth_client, create_user):
    """
    Deve retornar 400 ao tentar criar vínculo ativo duplicado (mesmo guardian + mesmo elder).
    """
    elder_user = create_user(email="elder_dup@example.com", role="ELDER")
    elder_profile = ElderProfile.objects.create(user=elder_user)

    client = auth_client(role="GUARDIAN", email="guardian_dup@example.com")
    guardian_user = User.objects.get(email="guardian_dup@example.com")
    guardian_profile, _ = GuardianProfile.objects.get_or_create(user=guardian_user)

    # Cria o vínculo ativo inicialmente (direto no banco)
    GuardianElderLink.objects.create(
        guardian=guardian_profile,
        elder=elder_profile,
        relationship="CHILD",
        is_active=True,
        can_view_medical=True,
        can_hire=True,
    )

    # Tenta criar novamente via API (deve falhar)
    resp = client.post(
        route_under_test,
        {
            "elder": elder_profile.id,
            "relationship": "CHILD",
            "is_active": True,
        },
        format="json",
    )

    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    # dependendo do serializer, pode vir em "elder" ou em "non_field_errors"
    details = body["error"]["details"]
    assert ("elder" in details) or ("non_field_errors" in details) or ("detail" in details)


@pytest.mark.django_db
def test_guardian_elder_link_forbidden_for_non_guardian(auth_client, create_user):
    """
    Usuário autenticado mas que não é GUARDIAN deve receber 403.
    """
    elder_user = create_user(email="elder_forbidden@example.com", role="ELDER")
    elder_profile = ElderProfile.objects.create(user=elder_user)

    # Autentica como ELDER (não GUARDIAN)
    client = auth_client(role="ELDER", email="elder_not_guardian@example.com")

    resp = client.post(
        route_under_test,
        {
            "elder": elder_profile.id,
            "relationship": "CHILD",
            "is_active": True,
        },
        format="json",
    )

    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "PERMISSION_DENIED"
