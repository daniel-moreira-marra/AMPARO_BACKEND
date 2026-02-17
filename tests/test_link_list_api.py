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
    user = create_user(email="elder_list@example.com", role="ELDER")
    profile = ElderProfile.objects.create(user=user)
    return user, profile

@pytest.fixture
def caregiver_setup(create_user):
    user = create_user(email="caregiver_list@example.com", role="CAREGIVER")
    profile = CaregiverProfile.objects.create(user=user)
    return user, profile

@pytest.fixture
def guardian_setup(create_user):
    user = create_user(email="guardian_list@example.com", role="GUARDIAN")
    profile = GuardianProfile.objects.create(user=user)
    return user, profile

@pytest.mark.django_db
class TestLinkList:

    def test_list_links_as_elder(self, auth_client, elder_setup, caregiver_setup, guardian_setup):
        elder_user, elder_profile = elder_setup
        cg_user, cg_profile = caregiver_setup
        gd_user, gd_profile = guardian_setup

        # Create links directly in DB
        CaregiverElderLink.objects.create(
            caregiver=cg_profile, 
            elder=elder_profile, 
            status="ACTIVE"
        )
        GuardianElderLink.objects.create(
            guardian=gd_profile, 
            elder=elder_profile, 
            status="PENDING",
            relationship="Child"
        )

        client = auth_client(role="ELDER", email=elder_user.email)
        resp = client.get(ROUTE)
        
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        
        # Verify annotation
        types = [item['link_type'] for item in data]
        assert "caregiver" in types
        assert "guardian" in types
        
        roles = [item['other_party_role'] for item in data]
        assert "Cuidador" in roles
        assert "Responsável" in roles

        # Verify IDs
        for item in data:
            assert item['elder_id'] == elder_profile.id
            if item['link_type'] == 'caregiver':
                assert item['other_party_id'] == cg_profile.id
            elif item['link_type'] == 'guardian':
                assert item['other_party_id'] == gd_profile.id

    def test_list_links_as_caregiver(self, auth_client, elder_setup, caregiver_setup):
        elder_user, elder_profile = elder_setup
        cg_user, cg_profile = caregiver_setup
        
        CaregiverElderLink.objects.create(
            caregiver=cg_profile, 
            elder=elder_profile, 
            status="ACTIVE"
        )

        client = auth_client(role="CAREGIVER", email=cg_user.email)
        resp = client.get(ROUTE)
        
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]['link_type'] == 'caregiver'
        assert data[0]['other_party_role'] == 'Idoso'
        # Check name logic (basic check)
        assert data[0]['other_party_name'] == elder_user.full_name
        assert data[0]['elder_id'] == elder_profile.id
        assert data[0]['other_party_id'] == elder_profile.id

    def test_list_empty(self, auth_client, elder_setup):
        elder_user, _ = elder_setup
        client = auth_client(role="ELDER", email=elder_user.email)
        resp = client.get(ROUTE)
        assert resp.status_code == 200
        assert len(resp.json()) == 0
