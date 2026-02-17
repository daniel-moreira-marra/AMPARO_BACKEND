
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from accounts.models import CaregiverProfile, GuardianProfile, ElderProfile
from links.models import CaregiverElderLink, GuardianElderLink

User = get_user_model()

@pytest.fixture
def elder_setup(create_user):
    user = create_user(email="elder_test@example.com", role="ELDER")
    profile = ElderProfile.objects.create(user=user)
    return user, profile

@pytest.fixture
def caregiver_setup(create_user):
    user = create_user(email="caregiver_test@example.com", role="CAREGIVER")
    profile = CaregiverProfile.objects.get_or_create(user=user)[0]
    return user, profile

@pytest.fixture
def guardian_setup(create_user, elder_setup):
    elder_user, elder_profile = elder_setup
    user = create_user(email="guardian_test@example.com", role="GUARDIAN")
    profile = GuardianProfile.objects.create(user=user)
    GuardianElderLink.objects.create(guardian=profile, elder=elder_profile)
    return user, profile, elder_profile

@pytest.mark.django_db
class TestCaregiverElderLinkRespond:
    def test_approve_by_elder_success(self, auth_client, elder_setup, caregiver_setup):
        elder_user, elder_profile = elder_setup
        cg_user, cg_profile = caregiver_setup
        
        link = CaregiverElderLink.objects.create(
            caregiver=cg_profile,
            elder=elder_profile,
            status=CaregiverElderLink.Status.PENDING,
            is_active=True
        )
        
        client = auth_client(email=elder_user.email, role="ELDER")
        resp = client.post("/api/v1/links/respond/", {
            "link_type": "caregiver",
            "link_id": link.id,
            "action": "approve"
        })
        
        assert resp.status_code == 200
        link.refresh_from_db()
        assert link.status == CaregiverElderLink.Status.ACTIVE
        assert link.is_active is True

    def test_reject_by_guardian_success(self, auth_client, elder_setup, caregiver_setup, create_user):
        elder_user, elder_profile = elder_setup
        cg_user, cg_profile = caregiver_setup
        
        # Create a guardian for the elder
        gd_user = create_user(email="gd_cg_resp@example.com", role="GUARDIAN")
        gd_profile = GuardianProfile.objects.create(user=gd_user)
        elder_profile.guardians.add(gd_profile)
        
        link = CaregiverElderLink.objects.create(
            caregiver=cg_profile,
            elder=elder_profile,
            status=CaregiverElderLink.Status.PENDING,
            is_active=True
        )
        
        client = auth_client(email=gd_user.email, role="GUARDIAN")
        resp = client.post("/api/v1/links/respond/", {
            "link_type": "caregiver",
            "link_id": link.id,
            "action": "reject"
        })
        
        assert resp.status_code == 200
        link.refresh_from_db()
        assert link.status == CaregiverElderLink.Status.CANCELLED
        assert link.is_active is False

    def test_unauthorized_respond_by_caregiver(self, auth_client, elder_setup, caregiver_setup):
        elder_user, elder_profile = elder_setup
        cg_user, cg_profile = caregiver_setup
        
        link = CaregiverElderLink.objects.create(
            caregiver=cg_profile,
            elder=elder_profile,
            status=CaregiverElderLink.Status.PENDING,
            is_active=True
        )
        
        client = auth_client(email=cg_user.email, role="CAREGIVER")
        resp = client.post("/api/v1/links/respond/", {
            "link_type": "caregiver",
            "link_id": link.id,
            "action": "approve"
        })
        
        assert resp.status_code == 403

    def test_respond_conflict_already_active(self, auth_client, elder_setup, caregiver_setup):
        elder_user, elder_profile = elder_setup
        cg_user, cg_profile = caregiver_setup
        
        link = CaregiverElderLink.objects.create(
            caregiver=cg_profile,
            elder=elder_profile,
            status=CaregiverElderLink.Status.ACTIVE,
            is_active=True
        )
        
        client = auth_client(email=elder_user.email, role="ELDER")
        resp = client.post("/api/v1/links/respond/", {
            "link_type": "caregiver",
            "link_id": link.id,
            "action": "approve"
        })
        
        assert resp.status_code == 400

    def test_link_not_found(self, auth_client, elder_setup):
        elder_user, elder_profile = elder_setup
        client = auth_client(email=elder_user.email, role="ELDER")
        resp = client.post("/api/v1/links/respond/", {
            "link_type": "caregiver",
            "link_id": 9999,
            "action": "approve"
        })
        assert resp.status_code == 404

    def test_create_link_always_pending(self, auth_client, elder_setup, caregiver_setup):
        elder_user, elder_profile = elder_setup
        cg_user, cg_profile = caregiver_setup
        
        client = auth_client(email=cg_user.email, role="CAREGIVER")
        payload = {
            "link_type": "caregiver",
            "elder": elder_profile.id,
        }
        resp = client.post("/api/v1/links/", payload)
        
        assert resp.status_code == 201
        link_id = resp.json()["data"]["id"]
        link = CaregiverElderLink.objects.get(id=link_id)
        assert link.status == CaregiverElderLink.Status.PENDING

    def test_prevent_duplicate_active_or_pending_link(self, auth_client, elder_setup, caregiver_setup):
        elder_user, elder_profile = elder_setup
        cg_user, cg_profile = caregiver_setup
        
        CaregiverElderLink.objects.create(
            caregiver=cg_profile,
            elder=elder_profile,
            status=CaregiverElderLink.Status.PENDING,
            is_active=True
        )
        
        client = auth_client(email=cg_user.email, role="CAREGIVER")
        payload = {
            "link_type": "caregiver",
            "elder": elder_profile.id
        }
        resp = client.post("/api/v1/links/", payload)
        
        assert resp.status_code == 400
        # Check standard wrapped error
        error_details = resp.json()["error"]["details"]
        assert "elder" in error_details
        assert "Já existe um vínculo ativo com este idoso." in error_details["elder"]


