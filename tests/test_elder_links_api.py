import pytest
from django.contrib.auth import get_user_model
from accounts.models import (
    ElderProfile, CaregiverProfile, GuardianProfile, 
    ProfessionalProfile, InstitutionProfile
)
from links.models import (
    CaregiverElderLink, 
    GuardianElderLink, 
    ProfessionalElderLink, 
    InstitutionElderLink
)

User = get_user_model()

@pytest.fixture
def elder_user(create_user):
    user = create_user(email="elder_test@example.com", role="ELDER")
    ElderProfile.objects.get_or_create(user=user)
    return user

@pytest.fixture
def other_elder_user(create_user):
    user = create_user(email="other_elder@example.com", role="ELDER")
    ElderProfile.objects.get_or_create(user=user)
    return user

@pytest.fixture
def caregiver_user(create_user):
    user = create_user(email="caregiver_test@example.com", role="CAREGIVER")
    CaregiverProfile.objects.get_or_create(user=user)
    return user

@pytest.fixture
def guardian_user(create_user):
    user = create_user(email="guardian_test@example.com", role="GUARDIAN")
    GuardianProfile.objects.get_or_create(user=user)
    return user

@pytest.fixture
def professional_user(create_user):
    user = create_user(email="prof_test@example.com", role="PROFESSIONAL")
    ProfessionalProfile.objects.get_or_create(user=user)
    return user

@pytest.fixture
def institution_user(create_user):
    user = create_user(email="inst_test@example.com", role="INSTITUTION")
    InstitutionProfile.objects.get_or_create(user=user)
    return user

@pytest.mark.django_db
class TestElderLinksAPI:
    def test_elder_list_all_links_consolidated(self, auth_client, elder_user, other_elder_user, caregiver_user, guardian_user, professional_user, institution_user):
        client = auth_client(email=elder_user.email, role="ELDER")
        
        # Create various links for the test elder
        CaregiverElderLink.objects.create(
            elder=elder_user.elder_profile,
            caregiver=caregiver_user.caregiver_profile,
            status="ACTIVE"
        )
        GuardianElderLink.objects.create(
            elder=elder_user.elder_profile,
            guardian=guardian_user.guardian_profile,
            status="ACTIVE",
            relationship="CHILD"
        )
        ProfessionalElderLink.objects.create(
            elder=elder_user.elder_profile,
            professional=professional_user.professional_profile,
            status="PENDING"
        )
        InstitutionElderLink.objects.create(
            elder=elder_user.elder_profile,
            institution=institution_user.institution_profile,
            status="ENDED"
        )
        
        # List all
        resp = client.get("/api/v1/links/")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 4
        
        # Verify types are present
        types = [item['link_type'] for item in data]
        assert 'caregiver' in types
        assert 'guardian' in types
        assert 'professional' in types
        assert 'institution' in types
