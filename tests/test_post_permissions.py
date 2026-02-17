import pytest
from django.contrib.auth import get_user_model
from posts.models import Post
from posts.enums import VisibilityScope, PostStatus
from links.models import CaregiverElderLink
from accounts.models.caregiver_profile import CaregiverProfile
from accounts.models.elder_profile import ElderProfile

User = get_user_model()

pytestmark = pytest.mark.django_db

def get_detail_url(post_id):
    return f"/api/v1/posts/my-posts/{post_id}/"

@pytest.fixture
def elder_user(create_user):
    user = create_user(email="elder@test.com", role="ELDER")
    ElderProfile.objects.get_or_create(user=user)
    return user

@pytest.fixture
def caregiver_user(create_user):
    user = create_user(email="caregiver@test.com", role="CAREGIVER")
    CaregiverProfile.objects.get_or_create(user=user)
    return user

@pytest.fixture
def stranger_user(create_user):
    return create_user(email="stranger@test.com", role="ELDER")

class TestPostPermissions:

    def test_anonymous_cannot_view_private_post(self, api_client, create_post, elder_user):
        post = create_post(author=elder_user, visibility_scope=VisibilityScope.PRIVATE, status=PostStatus.PUBLISHED)
        url = get_detail_url(post.id)
        
        resp = api_client.get(url)
        assert resp.status_code == 401 # Should require login first

    def test_owner_can_view_own_private_post(self, auth_client, create_post):
        # auth_client creates a user and authenticates
        client = auth_client(email="owner@test.com", role="ELDER")
        user = User.objects.get(email="owner@test.com")
        ElderProfile.objects.get_or_create(user=user)
        
        post = create_post(author=user, visibility_scope=VisibilityScope.PRIVATE, status=PostStatus.PUBLISHED)
        url = get_detail_url(post.id)
        
        resp = client.get(url)
        assert resp.status_code == 200

    def test_stranger_cannot_view_restricted_post(self, auth_client, create_post, elder_user):
        client = auth_client(email="stranger@test.com", role="CAREGIVER")
        CaregiverProfile.objects.get_or_create(user=User.objects.get(email="stranger@test.com"))
        
        post = create_post(author=elder_user, visibility_scope=VisibilityScope.CAREGIVERS, status=PostStatus.PUBLISHED)
        url = get_detail_url(post.id)
        
        resp = client.get(url)
        # In MyPostsViewSet, get_queryset filters by author, so it returns 404.
        # This confirms the "security by filtering" and also permission if it were accessible.
        assert resp.status_code == 404

    def test_caregiver_with_active_link_can_view_post(self, api_client, create_post, elder_user, caregiver_user):
        # We need a View that allows viewing other people's posts to truly test the permission class
        # since MyPostsViewSet is restricted by queryset.
        # For this test, let's assume we are testing the CanViewPost logic directly or via a mock view.
        
        # Create active link
        CaregiverElderLink.objects.create(
            elder=elder_user.elder_profile,
            caregiver=caregiver_user.caregiver_profile,
            status=CaregiverElderLink.Status.ACTIVE
        )
        
        post = create_post(author=elder_user, visibility_scope=VisibilityScope.CAREGIVERS, status=PostStatus.PUBLISHED)
        
        from posts.permissions import CanViewPost
        permission = CanViewPost()
        
        class MockRequest:
            user = caregiver_user
            
        assert permission.has_object_permission(MockRequest(), None, post) is True

    def test_caregiver_with_pending_link_cannot_view_post(self, create_post, elder_user, caregiver_user):
        # Create pending link
        CaregiverElderLink.objects.create(
            elder=elder_user.elder_profile,
            caregiver=caregiver_user.caregiver_profile,
            status=CaregiverElderLink.Status.PENDING
        )
        
        post = create_post(author=elder_user, visibility_scope=VisibilityScope.CAREGIVERS, status=PostStatus.PUBLISHED)
        
        from posts.permissions import CanViewPost
        permission = CanViewPost()
        
        class MockRequest:
            user = caregiver_user
            
        assert permission.has_object_permission(MockRequest(), None, post) is False

    def test_edit_only_allowed_for_owner(self, auth_client, create_post, elder_user):
        client = auth_client(email="other_elder@test.com", role="ELDER")
        other_user = User.objects.get(email="other_elder@test.com")
        ElderProfile.objects.get_or_create(user=other_user)
        
        post = create_post(author=elder_user, text="Original")
        url = get_detail_url(post.id)
        
        resp = client.patch(url, {"text": "Changed"}, format="json")
        assert resp.status_code == 404 # filtered out by queryset
