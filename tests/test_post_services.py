import pytest
from django.utils import timezone
from posts.services.post_services import create_post as post_create_service, delete_post
from posts.models import Post
from core.exceptions import domain as domain_exceptions
from core.events import _handlers

pytestmark = pytest.mark.django_db

def test_create_post_success(create_user):
    user = create_user(email="service_test@example.com")
    data = {"text": "Service Post", "visibility_scope": "PUBLIC"}
    
    post = post_create_service(actor=user, data=data)
    
    assert post.id is not None
    assert post.text == "Service Post"
    assert post.author == user
    assert post.published_at is not None

def test_create_post_missing_text(create_user):
    user = create_user(email="fail_test@example.com")
    data = {"text": ""}
    
    with pytest.raises(domain_exceptions.ValidationError) as excinfo:
        post_create_service(actor=user, data=data)
    
    assert excinfo.value.code == "missing_text"

def test_create_reply_success(create_user, create_post):
    user = create_user(email="reply_test@example.com")
    parent = create_post(author=user, text="Original")
    
    data = {"text": "Reply", "parent_post_id": parent.id}
    reply = post_create_service(actor=user, data=data)
    
    assert reply.parent_post == parent

def test_delete_post_success(create_user, create_post):
    user = create_user(email="delete_test@example.com")
    post = create_post(author=user, text="To be deleted")
    
    delete_post(actor=user, post_id=post.id)
    
    post.refresh_from_db()
    assert post.deleted_at is not None

def test_delete_post_permission_denied(create_user, create_post):
    user1 = create_user(email="u1@example.com")
    user2 = create_user(email="u2@example.com")
    post = create_post(author=user1, text="Not yours")
    
    with pytest.raises(domain_exceptions.PermissionDenied):
        delete_post(actor=user2, post_id=post.id)
