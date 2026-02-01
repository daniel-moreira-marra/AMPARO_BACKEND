import pytest
from posts.services.post_services import create_post, delete_post
from core.exceptions import domain as domain_exceptions
from posts.enums import VisibilityScope

@pytest.mark.django_db
@pytest.mark.unit
class TestPostService:
    """
    Testes de unidade para a camada de serviço de posts.
    """

    def test_create_post_success(self, caregiver):
        data = {
            "text": "Post de teste",
            "visibility_scope": VisibilityScope.PUBLIC
        }
        post = create_post(actor=caregiver, data=data)
        
        assert post.text == "Post de teste"
        assert post.author == caregiver
        assert post.published_at is not None

    def test_create_post_empty_text_raises_error(self, caregiver):
        data = {"text": "  "}
        with pytest.raises(domain_exceptions.ValidationError) as excinfo:
            create_post(actor=caregiver, data=data)
        assert excinfo.value.code == "missing_text"

    def test_delete_post_success(self, caregiver, post_factory):
        post = post_factory(author=caregiver)
        delete_post(actor=caregiver, post_id=post.id)
        
        post.refresh_from_db()
        assert post.deleted_at is not None

    def test_cannot_delete_other_users_post(self, caregiver, other_user, post_factory):
        post = post_factory(author=other_user)
        
        with pytest.raises(domain_exceptions.PermissionDenied):
            delete_post(actor=caregiver, post_id=post.id)

    def test_reply_to_deleted_post_raises_error(self, caregiver, post_factory):
        parent_post = post_factory(author=caregiver)
        # Soft delete manualmente para o teste
        from django.utils import timezone
        parent_post.deleted_at = timezone.now()
        parent_post.save()
        
        data = {
            "text": "Resposta",
            "parent_post_id": parent_post.id
        }
        
        with pytest.raises(domain_exceptions.ValidationError) as excinfo:
            create_post(actor=caregiver, data=data)
        assert excinfo.value.code == "inactive_parent"
