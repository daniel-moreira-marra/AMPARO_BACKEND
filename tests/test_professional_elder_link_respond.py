import pytest
from rest_framework import status
from accounts.models import (
    ElderProfile,
    ProfessionalProfile,
    GuardianProfile,
)
from links.models import ProfessionalElderLink, GuardianElderLink

@pytest.fixture
def elder_setup(create_user):
    user = create_user(email="elder_pro_test@example.com", role="ELDER")
    profile = ElderProfile.objects.create(user=user)
    return user, profile

@pytest.fixture
def professional_setup(create_user):
    user = create_user(email="pro_test@example.com", role="PROFESSIONAL")
    profile = ProfessionalProfile.objects.create(user=user)
    return user, profile

@pytest.fixture
def guardian_setup(create_user, elder_setup):
    elder_user, elder_profile = elder_setup
    user = create_user(email="guardian_pro_test@example.com", role="GUARDIAN")
    profile = GuardianProfile.objects.create(user=user)
    GuardianElderLink.objects.create(guardian=profile, elder=elder_profile, status=GuardianElderLink.Status.ACTIVE)
    return user, profile, elder_profile

@pytest.mark.django_db
class TestProfessionalElderLinkRespond:
    def test_approve_by_elder_success(self, auth_client, elder_setup, professional_setup):
        elder_user, elder_profile = elder_setup
        pro_user, pro_profile = professional_setup
        
        link = ProfessionalElderLink.objects.create(
            professional=pro_profile,
            elder=elder_profile,
            status=ProfessionalElderLink.Status.PENDING,
            is_active=True
        )
        
        client = auth_client(email=elder_user.email, role="ELDER")
        resp = client.post("/api/v1/links/respond/", {
            "link_type": "professional",
            "link_id": link.id,
            "action": "approve"
        })
        
        assert resp.status_code == 200
        link.refresh_from_db()
        assert link.status == ProfessionalElderLink.Status.ACTIVE
        assert link.is_active is True

    def test_reject_by_guardian_success(self, auth_client, guardian_setup, professional_setup):
        guardian_user, guardian_profile, elder_profile = guardian_setup
        pro_user, pro_profile = professional_setup
        
        link = ProfessionalElderLink.objects.create(
            professional=pro_profile,
            elder=elder_profile,
            status=ProfessionalElderLink.Status.PENDING,
            is_active=True
        )
        
        client = auth_client(email=guardian_user.email, role="GUARDIAN")
        resp = client.post("/api/v1/links/respond/", {
            "link_type": "professional",
            "link_id": link.id,
            "action": "reject"
        })
        
        assert resp.status_code == 200
        link.refresh_from_db()
        assert link.status == ProfessionalElderLink.Status.CANCELLED
        assert link.is_active is False

    def test_create_link_always_pending(self, auth_client, elder_setup, professional_setup):
        elder_user, elder_profile = elder_setup
        pro_user, pro_profile = professional_setup
        
        client = auth_client(email=pro_user.email, role="PROFESSIONAL")
        payload = {
            "link_type": "professional",
            "elder": elder_profile.id,
            "service_mode": "HOME",
        }
        resp = client.post("/api/v1/links/", payload)
        
        assert resp.status_code == 201
        link_id = resp.json()["data"]["id"]
        link = ProfessionalElderLink.objects.get(id=link_id)
        assert link.status == ProfessionalElderLink.Status.PENDING
        assert link.is_active is True

