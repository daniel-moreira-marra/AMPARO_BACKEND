import pytest
from django.contrib.auth import get_user_model
from links.models import (
    CaregiverElderLink,
    GuardianElderLink,
    ProfessionalElderLink,
    InstitutionElderLink,
)
from accounts.models import (
    ElderProfile,
    CaregiverProfile,
    GuardianProfile,
    ProfessionalProfile,
    InstitutionProfile,
)

User = get_user_model()
ROUTE = "/api/v1/links/"

@pytest.fixture
def elder_setup(create_user):
    user = create_user(email="elder_gen@example.com", role="ELDER")
    profile = ElderProfile.objects.create(user=user)
    return user, profile

@pytest.fixture
def caregiver_setup(create_user):
    user = create_user(email="caregiver_gen@example.com", role="CAREGIVER")
    profile = CaregiverProfile.objects.create(user=user)
    return user, profile

@pytest.fixture
def guardian_setup(create_user):
    user = create_user(email="guardian_gen@example.com", role="GUARDIAN")
    profile = GuardianProfile.objects.create(user=user)
    return user, profile

@pytest.fixture
def professional_setup(create_user):
    user = create_user(email="professional_gen@example.com", role="PROFESSIONAL")
    profile = ProfessionalProfile.objects.create(user=user)
    return user, profile

@pytest.fixture
def institution_setup(create_user):
    user = create_user(email="institution_gen@example.com", role="INSTITUTION")
    profile = InstitutionProfile.objects.create(user=user)
    return user, profile

@pytest.mark.django_db
class TestGenericLinkCreate:

    def test_create_caregiver_link_success(self, auth_client, elder_setup, caregiver_setup):
        elder_user, elder_profile = elder_setup
        cg_user, cg_profile = caregiver_setup

        client = auth_client(role="CAREGIVER", email=cg_user.email)
        payload = {
            "link_type": "caregiver",
            "elder": elder_profile.id,
            "agreed_hourly_rate": "50.00",
            "notes": "Testing generic link creation"
        }

        resp = client.post(ROUTE, payload, format="json")
        assert resp.status_code == 201
        
        link = CaregiverElderLink.objects.get(caregiver=cg_profile, elder=elder_profile)
        assert link.status == CaregiverElderLink.Status.PENDING
        assert link.agreed_hourly_rate == 50.00
        assert link.notes == "Testing generic link creation"

    def test_create_guardian_link_success(self, auth_client, elder_setup, guardian_setup):
        elder_user, elder_profile = elder_setup
        gd_user, gd_profile = guardian_setup

        client = auth_client(role="GUARDIAN", email=gd_user.email)
        payload = {
            "link_type": "guardian",
            "elder": elder_profile.id,
            "relationship": "CHILD",
            "is_legal_guardian": True
        }

        resp = client.post(ROUTE, payload, format="json")
        assert resp.status_code == 201

        link = GuardianElderLink.objects.get(guardian=gd_profile, elder=elder_profile)
        assert link.status == GuardianElderLink.Status.PENDING
        assert link.relationship == "CHILD"
        assert link.is_legal_guardian is True

    def test_create_professional_link_success(self, auth_client, elder_setup, professional_setup):
        elder_user, elder_profile = elder_setup
        prof_user, prof_profile = professional_setup

        client = auth_client(role="PROFESSIONAL", email=prof_user.email)
        payload = {
            "link_type": "professional",
            "elder": elder_profile.id,
            "service_mode": "HOME",
            "goals": "Generic goals"
        }

        resp = client.post(ROUTE, payload, format="json")
        assert resp.status_code == 201
        
        link = ProfessionalElderLink.objects.get(professional=prof_profile, elder=elder_profile)
        assert link.status == ProfessionalElderLink.Status.PENDING
        assert link.service_mode == "HOME"

    def test_create_institution_link_success(self, auth_client, elder_setup, institution_setup):
        elder_user, elder_profile = elder_setup
        inst_user, inst_profile = institution_setup

        client = auth_client(role="INSTITUTION", email=inst_user.email)
        payload = {
            "link_type": "institution",
            "elder": elder_profile.id,
            "room": "101",
            "bed": "A"
        }

        resp = client.post(ROUTE, payload, format="json")
        assert resp.status_code == 201

        link = InstitutionElderLink.objects.get(institution=inst_profile, elder=elder_profile)
        assert link.status == InstitutionElderLink.Status.PENDING
        assert link.room == "101"

    def test_create_link_invalid_type(self, auth_client, elder_setup, caregiver_setup):
        cg_user, _ = caregiver_setup
        client = auth_client(role="CAREGIVER", email=cg_user.email)
        payload = {
            "link_type": "invalid_type",
            "elder": elder_setup[1].id
        }
        resp = client.post(ROUTE, payload, format="json")
        assert resp.status_code == 400
        body = resp.json()
        assert "link_type" in body["error"]["details"]

    def test_create_link_wrong_role(self, auth_client, elder_setup, caregiver_setup):
        # Caregiver trying to create generic institution link
        cg_user, _ = caregiver_setup
        client = auth_client(role="CAREGIVER", email=cg_user.email)
        payload = {
            "link_type": "institution",
            "elder": elder_setup[1].id
        }
        resp = client.post(ROUTE, payload, format="json")
        assert resp.status_code == 400
        # Serializer custom validation should catch this
        body = resp.json()
        assert "non_field_errors" in body["error"]["details"]

