import pytest
from accounts.models import (
    ProfessionalProfile,
    ElderProfile,
    CaregiverProfile,
    GuardianProfile,
    InstitutionProfile,
)
from django.contrib.auth import get_user_model

User = get_user_model()

URL = "/api/v1/search/"


# ---------------------------------------------------------------------------#
# Helpers
# ---------------------------------------------------------------------------#

def _make_user(role, email, full_name="Test User"):
    return User.objects.create_user(
        email=email,
        password="pass123",
        role=role,
        full_name=full_name,
    )


# ---------------------------------------------------------------------------#
# Sem parâmetros – retorna todos os tipos
# ---------------------------------------------------------------------------#

@pytest.mark.django_db
def test_search_no_params_returns_success(api_client):
    resp = api_client.get(URL)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "count" in body["data"]
    assert "results" in body["data"]


# ---------------------------------------------------------------------------#
# Filtrar por role
# ---------------------------------------------------------------------------#

@pytest.mark.django_db
def test_search_by_role_professional_returns_only_professionals(api_client):
    user_prof = _make_user("PROFESSIONAL", "prof_search@example.com", "Dr. Carlos")
    ProfessionalProfile.objects.create(
        user=user_prof,
        profession="PHYSIOTHERAPIST",
    )
    # idoso não deve aparecer
    user_elder = _make_user("ELDER", "elder_search@example.com", "Dona Maria")
    ElderProfile.objects.create(user=user_elder)

    resp = api_client.get(URL, {"role": "PROFESSIONAL"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["role"] == "PROFESSIONAL"
    result_ids = [r["id"] for r in data["results"]]
    assert user_prof.professional_profile.id in result_ids
    # Elder não deve aparecer
    for item in data["results"]:
        assert item["role"] == "PROFESSIONAL"


@pytest.mark.django_db
def test_search_by_role_elder_returns_only_elders(api_client):
    user_elder = _make_user("ELDER", "elder2_search@example.com", "Sr. José")
    ElderProfile.objects.create(user=user_elder)

    resp = api_client.get(URL, {"role": "ELDER"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["role"] == "ELDER"
    assert any(r["full_name"] == "Sr. José" for r in data["results"])


@pytest.mark.django_db
def test_search_by_role_caregiver(api_client):
    user = _make_user("CAREGIVER", "caregiver_search@example.com", "Ana Cuidadora")
    CaregiverProfile.objects.create(user=user, bio="Ampla experiência")

    resp = api_client.get(URL, {"role": "CAREGIVER"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["role"] == "CAREGIVER"
    assert any(r["full_name"] == "Ana Cuidadora" for r in data["results"])


# ---------------------------------------------------------------------------#
# Busca textual – campo nome
# ---------------------------------------------------------------------------#

@pytest.mark.django_db
def test_search_q_matches_full_name(api_client):
    user = _make_user("PROFESSIONAL", "prof_q@example.com", "João Fisioterapeuta")
    ProfessionalProfile.objects.create(user=user, profession="PHYSIOTHERAPIST")

    resp = api_client.get(URL, {"role": "PROFESSIONAL", "q": "João"})
    assert resp.status_code == 200
    results = resp.json()["data"]["results"]
    assert any(r["full_name"] == "João Fisioterapeuta" for r in results)


@pytest.mark.django_db
def test_search_q_matches_profession_field(api_client):
    user = _make_user("PROFESSIONAL", "prof_q2@example.com", "Maria Terapeuta")
    ProfessionalProfile.objects.create(user=user, profession="OCCUPATIONAL_THERAPIST")

    # pesquisa pelo valor do campo `profession` (conteúdo do CharField)
    resp = api_client.get(URL, {"role": "PROFESSIONAL", "q": "OCCUPATIONAL"})
    assert resp.status_code == 200
    results = resp.json()["data"]["results"]
    assert any(r["full_name"] == "Maria Terapeuta" for r in results)


@pytest.mark.django_db
def test_search_q_matches_institution_legal_name(api_client):
    user = _make_user("INSTITUTION", "inst_search@example.com", "ILPI Horizonte")
    InstitutionProfile.objects.create(
        user=user,
        legal_name="ILPI Horizonte Ltda.",
        institution_type="ILPI",
    )

    resp = api_client.get(URL, {"role": "INSTITUTION", "q": "Horizonte"})
    assert resp.status_code == 200
    results = resp.json()["data"]["results"]
    assert any(r["legal_name"] == "ILPI Horizonte Ltda." for r in results)


# ---------------------------------------------------------------------------#
# Sem resultados
# ---------------------------------------------------------------------------#

@pytest.mark.django_db
def test_search_no_match_returns_empty(api_client):
    resp = api_client.get(URL, {"role": "PROFESSIONAL", "q": "XKCD_TERM_NAO_EXISTE_123"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["count"] == 0
    assert data["results"] == []


# ---------------------------------------------------------------------------#
# Role inválido
# ---------------------------------------------------------------------------#

@pytest.mark.django_db
def test_search_invalid_role_returns_400(api_client):
    resp = api_client.get(URL, {"role": "INVALIDO"})
    assert resp.status_code == 400
    body = resp.json()
    assert body["error"]["code"] == "INVALID_ROLE"


# ---------------------------------------------------------------------------#
# Busca global (sem role) – retorna lista plana com discriminador
# ---------------------------------------------------------------------------#

@pytest.mark.django_db
def test_search_global_flat_list_has_role_key(api_client):
    user_prof = _make_user("PROFESSIONAL", "prof_global@example.com", "Dr. Global")
    ProfessionalProfile.objects.create(user=user_prof, profession="PSYCHOLOGIST")
    user_elder = _make_user("ELDER", "elder_global@example.com", "Sr. Global")
    ElderProfile.objects.create(user=user_elder)

    resp = api_client.get(URL, {"q": "Global"})
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["count"] >= 2
    roles_present = {r["role"] for r in data["results"]}
    assert "PROFESSIONAL" in roles_present
    assert "ELDER" in roles_present
