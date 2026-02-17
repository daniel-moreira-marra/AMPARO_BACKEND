import pytest
from rest_framework import status
from accounts.models import (
    ElderProfile,
    InstitutionProfile,
    GuardianProfile,
)
from links.models import InstitutionElderLink, GuardianElderLink

@pytest.fixture
def elder_setup(create_user):
    user = create_user(email="elder_inst_test@example.com", role="ELDER")
    profile = ElderProfile.objects.create(user=user)
    return user, profile

@pytest.fixture
def institution_setup(create_user):
    user = create_user(email="inst_test@example.com", role="INSTITUTION")
    profile = InstitutionProfile.objects.create(user=user)
    return user, profile

@pytest.fixture
def guardian_setup(create_user, elder_setup):
    elder_user, elder_profile = elder_setup
    user = create_user(email="guardian_inst_test@example.com", role="GUARDIAN")
    profile = GuardianProfile.objects.create(user=user)
    GuardianElderLink.objects.create(guardian=profile, elder=elder_profile, status=GuardianElderLink.Status.ACTIVE)
    return user, profile, elder_profile

@pytest.mark.django_db
class TestInstitutionElderLinkRespond:
    def test_approve_by_elder_success(self, auth_client, elder_setup, institution_setup):
        elder_user, elder_profile = elder_setup
        inst_user, inst_profile = institution_setup
        
        link = InstitutionElderLink.objects.create(
            institution=inst_profile,
            elder=elder_profile,
            status=InstitutionElderLink.Status.PENDING,
            is_active=True
        )
        
        client = auth_client(email=elder_user.email, role="ELDER")
        resp = client.post("/api/v1/links/respond/", {
            "link_type": "institution",
            "link_id": link.id,
            "action": "approve"
        })
        
        assert resp.status_code == 200
        link.refresh_from_db()
        assert link.status == InstitutionElderLink.Status.ACTIVE
        assert link.is_active is True

    def test_create_link_always_pending(self, auth_client, elder_setup, institution_setup):
        elder_user, elder_profile = elder_setup
        inst_user, inst_profile = institution_setup
        
        client = auth_client(email=inst_user.email, role="INSTITUTION")
        payload = {
            "link_type": "institution",
            "elder": elder_profile.id,
        }
        resp = client.post("/api/v1/links/", payload)
        
        assert resp.status_code == 201
        link_id = resp.json()["data"]["id"]
        link = InstitutionElderLink.objects.get(id=link_id)
        assert link.status == InstitutionElderLink.Status.PENDING
        assert link.is_active is True

