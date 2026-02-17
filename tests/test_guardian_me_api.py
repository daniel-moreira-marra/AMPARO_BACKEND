import pytest
from accounts.models import GuardianProfile

@pytest.mark.django_db
def test_guardian_me_requires_auth(api_client):
    resp = api_client.get("/api/v1/guardians/me/")
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "NOT_AUTHENTICATED"

@pytest.mark.django_db
def test_guardian_me_forbids_non_guardian(auth_client):
    client = auth_client(role="ELDER", email="elder@example.com")
    resp = client.get("/api/v1/guardians/me/")
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "PERMISSION_DENIED"

@pytest.mark.django_db
def test_guardian_me_get_returns_profile(auth_client):
    client = auth_client(role="GUARDIAN", email="guardian@example.com")

    # GET deve criar o profile se não existir (get_or_create)
    resp = client.get("/api/v1/guardians/me/")
    assert resp.status_code == 200

    body = resp.json()["data"]
    assert "relationship" in body
    assert "is_legal_guardian" in body
    assert "preferred_contact" in body

    profile = GuardianProfile.objects.get(user__email="guardian@example.com")
    assert profile is not None

@pytest.mark.django_db
def test_guardian_me_patch_updates_profile_fields(auth_client):
    client = auth_client(role="GUARDIAN", email="guardian2@example.com")

    # Cria profile
    client.get("/api/v1/guardians/me/")

    patch_resp = client.patch(
        "/api/v1/guardians/me/",
        {
            "relationship": "CHILD",
            "is_legal_guardian": True,
            "preferred_contact": "WHATSAPP"
        },
        format="json",
    )
    assert patch_resp.status_code == 200
    body = patch_resp.json()["data"]
    assert body["relationship"] == "CHILD"
    assert body["is_legal_guardian"] is True
    assert body["preferred_contact"] == "WHATSAPP"

    profile = GuardianProfile.objects.get(user__email="guardian2@example.com")
    assert profile.relationship == "CHILD"
    assert profile.is_legal_guardian is True
    assert profile.preferred_contact == "WHATSAPP"

@pytest.mark.django_db
def test_guardian_me_put_replaces_profile(auth_client):
    client = auth_client(role="GUARDIAN", email="guardian3@example.com")

    # Cria profile
    client.get("/api/v1/guardians/me/")

    put_resp = client.put(
        "/api/v1/guardians/me/",
        {
            "relationship": "RELATIVE",
            "is_legal_guardian": False,
            "preferred_contact": "EMAIL"
        },
        format="json",
    )
    assert put_resp.status_code == 200
    body = put_resp.json()["data"]

    assert body["relationship"] == "RELATIVE"
    assert body["is_legal_guardian"] is False
    assert body["preferred_contact"] == "EMAIL"

    profile = GuardianProfile.objects.get(user__email="guardian3@example.com")
    assert profile.relationship == "RELATIVE"
