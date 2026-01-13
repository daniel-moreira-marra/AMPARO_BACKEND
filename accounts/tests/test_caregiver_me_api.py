import pytest

from accounts.models import CaregiverProfile, CaregiverCareType
from accounts.models.enums import CareType


@pytest.mark.django_db
def test_caregiver_me_requires_auth(api_client):
    resp = api_client.get("/api/v1/caregivers/me/")
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "NOT_AUTHENTICATED"


@pytest.mark.django_db
def test_caregiver_me_forbids_non_caregiver(auth_client):
    client = auth_client(role="ELDER", email="elder@example.com")
    resp = client.get("/api/v1/caregivers/me/")
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "PERMISSION_DENIED"


@pytest.mark.django_db
def test_caregiver_me_get_returns_profile_and_care_types(auth_client):
    client = auth_client(role="CAREGIVER", email="cg1@example.com")

    # GET deve criar o profile se não existir (get_or_create)
    resp = client.get("/api/v1/caregivers/me/")
    assert resp.status_code == 200

    body = resp.json()
    assert "care_types" in body
    assert isinstance(body["care_types"], list)

    profile = CaregiverProfile.objects.get(user__email="cg1@example.com")
    assert profile is not None


@pytest.mark.django_db
def test_caregiver_me_patch_updates_profile_fields(auth_client):
    client = auth_client(role="CAREGIVER", email="cg2@example.com")

    # Cria profile
    client.get("/api/v1/caregivers/me/")

    patch_resp = client.patch(
        "/api/v1/caregivers/me/",
        {"bio": "Cuidador com 3 anos de experiência.", "city": "São Paulo", "state": "SP"},
        format="json",
    )
    assert patch_resp.status_code == 200
    body = patch_resp.json()
    assert body["bio"] == "Cuidador com 3 anos de experiência."
    assert body["city"] == "São Paulo"
    assert body["state"] == "SP"

    profile = CaregiverProfile.objects.get(user__email="cg2@example.com")
    assert profile.bio == "Cuidador com 3 anos de experiência."
    assert profile.city == "São Paulo"
    assert profile.state == "SP"


@pytest.mark.django_db
def test_caregiver_me_patch_syncs_care_types(auth_client):
    client = auth_client(role="CAREGIVER", email="cg3@example.com")

    # Cria profile
    client.get("/api/v1/caregivers/me/")
    profile = CaregiverProfile.objects.get(user__email="cg3@example.com")

    # Adiciona inicialmente HOME e HOSPITAL
    resp1 = client.patch(
        "/api/v1/caregivers/me/",
        {"care_types_input": [CareType.HOME, CareType.HOSPITAL]},
        format="json",
    )
    assert resp1.status_code == 200
    assert set(resp1.json()["care_types"]) == {CareType.HOME, CareType.HOSPITAL}

    assert set(
        CaregiverCareType.objects.filter(caregiver=profile).values_list("care_type", flat=True)
    ) == {CareType.HOME, CareType.HOSPITAL}

    # Atualiza para HOME e NIGHT_SHIFT (remove HOSPITAL)
    resp2 = client.patch(
        "/api/v1/caregivers/me/",
        {"care_types_input": [CareType.HOME, CareType.NIGHT_SHIFT]},
        format="json",
    )
    assert resp2.status_code == 200
    assert set(resp2.json()["care_types"]) == {CareType.HOME, CareType.NIGHT_SHIFT}

    assert set(
        CaregiverCareType.objects.filter(caregiver=profile).values_list("care_type", flat=True)
    ) == {CareType.HOME, CareType.NIGHT_SHIFT}


@pytest.mark.django_db
def test_caregiver_me_put_replaces_profile(auth_client):
    client = auth_client(role="CAREGIVER", email="cg4@example.com")

    # Cria profile
    client.get("/api/v1/caregivers/me/")

    put_resp = client.put(
        "/api/v1/caregivers/me/",
        {
            "bio": "Cuidador disponível para plantões.",
            "experience_years": 5,
            "is_available": True,
            "city": "Campinas",
            "state": "SP",
            "care_types_input": [CareType.DAY_SHIFT, CareType.COMPANION],
        },
        format="json",
    )
    assert put_resp.status_code == 200
    body = put_resp.json()

    assert body["bio"] == "Cuidador disponível para plantões."
    assert body["experience_years"] == 5
    assert body["is_available"] is True
    assert body["city"] == "Campinas"
    assert body["state"] == "SP"
    assert set(body["care_types"]) == {CareType.DAY_SHIFT, CareType.COMPANION}

    profile = CaregiverProfile.objects.get(user__email="cg4@example.com")
    assert profile.experience_years == 5

    assert set(
        CaregiverCareType.objects.filter(caregiver=profile).values_list("care_type", flat=True)
    ) == {CareType.DAY_SHIFT, CareType.COMPANION}


@pytest.mark.django_db
def test_caregiver_me_rejects_invalid_care_type(auth_client):
    client = auth_client(role="CAREGIVER", email="cg_invalid@example.com")

    # Cria profile
    client.get("/api/v1/caregivers/me/")

    resp = client.patch(
        "/api/v1/caregivers/me/",
        {"care_types_input": ["INVALID_TYPE"]},
        format="json",
    )

    assert resp.status_code == 400

    body = resp.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert "care_types_input" in body["error"]["details"]
