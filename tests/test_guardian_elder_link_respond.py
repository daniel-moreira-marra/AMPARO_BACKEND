import pytest
from rest_framework import status
from accounts.models import (
    ElderProfile,
    GuardianProfile,
)
from links.models import GuardianElderLink

@pytest.fixture
def elder_setup(create_user):
    user = create_user(email="elder_gd_test@example.com", role="ELDER")
    profile = ElderProfile.objects.create(user=user)
    return user, profile

@pytest.fixture
def guardian_setup(create_user):
    user = create_user(email="gd_test@example.com", role="GUARDIAN")
    profile = GuardianProfile.objects.create(user=user)
    return user, profile

@pytest.mark.django_db
class TestGuardianElderLinkRespond:
    def test_approve_by_elder_success(self, auth_client, elder_setup, guardian_setup):
        elder_user, elder_profile = elder_setup
        gd_user, gd_profile = guardian_setup
        
        link = GuardianElderLink.objects.create(
            guardian=gd_profile,
            elder=elder_profile,
            status=GuardianElderLink.Status.PENDING,
            is_active=True
        )
        
        client = auth_client(email=elder_user.email, role="ELDER")
        resp = client.post("/api/v1/links/respond/", {
            "link_type": "guardian",
            "link_id": link.id,
            "action": "approve"
        })
        
        assert resp.status_code == 200
        link.refresh_from_db()
        assert link.status == GuardianElderLink.Status.ACTIVE
        assert link.is_active is True

    def test_create_link_always_pending(self, auth_client, elder_setup, guardian_setup):
        elder_user, elder_profile = elder_setup
        gd_user, gd_profile = guardian_setup
        
        client = auth_client(email=gd_user.email, role="GUARDIAN")
        payload = {
            "link_type": "guardian",
            "elder": elder_profile.id,
            "relationship": "CHILD"
        }
        resp = client.post("/api/v1/links/", payload)
        
        assert resp.status_code == 201
        link_id = resp.json()["data"]["id"]
        link = GuardianElderLink.objects.get(id=link_id)
        assert link.status == GuardianElderLink.Status.PENDING
        assert link.is_active is True

