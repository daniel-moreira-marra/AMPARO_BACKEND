import pytest
from accounts.models import (
    ProfessionalProfile,
    CaregiverProfile,
    InstitutionProfile,
)
from django.contrib.auth import get_user_model

User = get_user_model()

URL = "/api/v1/search/"

def _make_user(role, email, full_name="Test User", city="", state=""):
    return User.objects.create_user(
        email=email,
        password="pass123",
        role=role,
        full_name=full_name,
        city=city,
        state=state,
    )


@pytest.mark.django_db
def test_search_filter_by_city_and_state(api_client):
    user_sp = _make_user("PROFESSIONAL", "prof_sp@example.com", "Dr. SP", city="São Paulo", state="SP")
    ProfessionalProfile.objects.create(user=user_sp, profession="PHYSIOTHERAPIST")

    user_rj = _make_user("PROFESSIONAL", "prof_rj@example.com", "Dr. RJ", city="Rio de Janeiro", state="RJ")
    ProfessionalProfile.objects.create(user=user_rj, profession="NUTRITIONIST")

    # Search by City
    resp_city = api_client.get(URL, {"city": "São Paulo"})
    assert resp_city.status_code == 200
    data_city = resp_city.json()["data"]["results"]
    assert len(data_city) == 1
    assert data_city[0]["full_name"] == "Dr. SP"

    # Search by State
    resp_state = api_client.get(URL, {"state": "RJ"})
    assert resp_state.status_code == 200
    data_state = resp_state.json()["data"]["results"]
    assert len(data_state) == 1
    assert data_state[0]["full_name"] == "Dr. RJ"


@pytest.mark.django_db
def test_search_professional_by_price_range(api_client):
    user_cheap = _make_user("PROFESSIONAL", "cheap@example.com", "Dr. Cheap")
    ProfessionalProfile.objects.create(user=user_cheap, profession="PHYSIOTHERAPIST", hourly_rate=50.00)

    user_expensive = _make_user("PROFESSIONAL", "expensive@example.com", "Dr. Expensive")
    ProfessionalProfile.objects.create(user=user_expensive, profession="PHYSIOTHERAPIST", hourly_rate=200.00)

    # Min Price
    resp_min = api_client.get(URL, {"role": "PROFESSIONAL", "min_price": "100"})
    assert resp_min.status_code == 200
    data_min = resp_min.json()["data"]["results"]
    assert len(data_min) == 1
    assert data_min[0]["full_name"] == "Dr. Expensive"

    # Max Price
    resp_max = api_client.get(URL, {"role": "PROFESSIONAL", "max_price": "100"})
    assert resp_max.status_code == 200
    data_max = resp_max.json()["data"]["results"]
    assert len(data_max) == 1
    assert data_max[0]["full_name"] == "Dr. Cheap"


@pytest.mark.django_db
def test_search_by_availability(api_client):
    user_avail = _make_user("CAREGIVER", "avail@example.com", "Avail")
    CaregiverProfile.objects.create(user=user_avail, is_available=True)

    user_unavail = _make_user("CAREGIVER", "unavail@example.com", "Unavail")
    CaregiverProfile.objects.create(user=user_unavail, is_available=False)

    # Search Available
    resp_avail = api_client.get(URL, {"role": "CAREGIVER", "is_available": "true"})
    assert resp_avail.status_code == 200
    data_avail = resp_avail.json()["data"]["results"]
    assert len(data_avail) == 1
    assert data_avail[0]["full_name"] == "Avail"
    assert data_avail[0]["is_available"] is True

    # Search Unavailable
    resp_unavail = api_client.get(URL, {"role": "CAREGIVER", "is_available": "false"})
    assert resp_unavail.status_code == 200
    data_unavail = resp_unavail.json()["data"]["results"]
    assert len(data_unavail) == 1
    assert data_unavail[0]["full_name"] == "Unavail"
    assert data_unavail[0]["is_available"] is False


@pytest.mark.django_db
def test_search_professional_by_profession_and_service_mode(api_client):
    user_physio = _make_user("PROFESSIONAL", "physio@example.com", "Fisio")
    ProfessionalProfile.objects.create(user=user_physio, profession="PHYSIOTHERAPIST", service_mode="HOME")

    user_nutri = _make_user("PROFESSIONAL", "nutri@example.com", "Nutri")
    ProfessionalProfile.objects.create(user=user_nutri, profession="NUTRITIONIST", service_mode="REMOTE")

    # Search by Profession
    resp_prof = api_client.get(URL, {"role": "PROFESSIONAL", "profession": "PHYSIOTHERAPIST"})
    assert resp_prof.status_code == 200
    data_prof = resp_prof.json()["data"]["results"]
    assert len(data_prof) == 1
    assert data_prof[0]["full_name"] == "Fisio"

    # Search by Service Mode
    resp_mode = api_client.get(URL, {"role": "PROFESSIONAL", "service_mode": "REMOTE"})
    assert resp_mode.status_code == 200
    data_mode = resp_mode.json()["data"]["results"]
    assert len(data_mode) == 1
    assert data_mode[0]["full_name"] == "Nutri"
