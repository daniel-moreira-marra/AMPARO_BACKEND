import pytest
from accounts.models import ElderProfile


@pytest.mark.django_db
def test_elder_me_requires_auth(api_client):
    resp = api_client.get("/api/v1/elders/me/")
    assert resp.status_code == 401


@pytest.mark.django_db
def test_elder_me_forbids_non_elder(auth_client):
    client = auth_client(role="CAREGIVER", email="caregiver@example.com")
    resp = client.get("/api/v1/elders/me/")
    assert resp.status_code == 403


@pytest.mark.django_db
def test_elder_me_get_returns_profile(auth_client):
    client = auth_client(role="ELDER", email="elder1@example.com")

    # O endpoint cria o profile se não existir (get_or_create), então GET deve funcionar.
    resp = client.get("/api/v1/elders/me/")
    assert resp.status_code == 200

    body = resp.json()
    assert "birth_date" in body
    assert "medical_notes" in body

    # Confirma que existe no banco
    assert ElderProfile.objects.filter(user__email="elder1@example.com").exists()


@pytest.mark.django_db
def test_elder_me_patch_updates_fields(auth_client):
    client = auth_client(role="ELDER", email="elder2@example.com")

    # Garante que o profile existe
    client.get("/api/v1/elders/me/")

    patch_resp = client.patch(
        "/api/v1/elders/me/",
        {"medical_notes": "Precisa de auxílio para medicação."},
        format="json",
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["medical_notes"] == "Precisa de auxílio para medicação."

    profile = ElderProfile.objects.get(user__email="elder2@example.com")
    assert profile.medical_notes == "Precisa de auxílio para medicação."


@pytest.mark.django_db
def test_elder_me_put_replaces_profile(auth_client):
    client = auth_client(role="ELDER", email="elder3@example.com")

    # Cria profile
    client.get("/api/v1/elders/me/")

    put_resp = client.put(
        "/api/v1/elders/me/",
        {
            "birth_date": "1950-01-01",
            "medical_notes": "Histórico: hipertensão.",
        },
        format="json",
    )
    assert put_resp.status_code == 200
    body = put_resp.json()
    assert body["birth_date"] == "1950-01-01"
    assert body["medical_notes"] == "Histórico: hipertensão."

    profile = ElderProfile.objects.get(user__email="elder3@example.com")
    assert str(profile.birth_date) == "1950-01-01"
    assert profile.medical_notes == "Histórico: hipertensão."
