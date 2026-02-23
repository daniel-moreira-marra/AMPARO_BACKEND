import pytest
from django.urls import reverse
from rest_framework import status

from posts.models import PostComment


@pytest.mark.django_db
class TestPostCommentAPI:
    def test_comment_requires_authentication(self, api_client, caregiver, post_factory):
        post = post_factory(author=caregiver, text="Post sem auth")
        url = reverse("post-comment-create", kwargs={"post_id": post.id})

        response = api_client.post(url, {"content": "Comentário"}, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_comment_post_success(self, api_client, caregiver, elder, post_factory):
        post = post_factory(author=caregiver, text="Post para comentário", comments_count=0)
        url = reverse("post-comment-create", kwargs={"post_id": post.id})
        api_client.force_authenticate(user=elder)

        response = api_client.post(url, {"content": "  Excelente post!  "}, format="json")

        post.refresh_from_db()
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True
        assert response.data["data"]["post_id"] == post.id
        assert response.data["data"]["user"] == elder.id
        assert response.data["data"]["user_id"] == elder.id
        assert response.data["data"]["content"] == "Excelente post!"
        assert response.data["data"]["comments_count"] == 1
        assert post.comments_count == 1
        assert PostComment.objects.filter(user=elder, post=post, content="Excelente post!").exists()

    def test_comment_post_not_found_returns_404(self, api_client, elder):
        api_client.force_authenticate(user=elder)
        url = reverse("post-comment-create", kwargs={"post_id": 999999})

        response = api_client.post(url, {"content": "Comentário"}, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["success"] is False
        assert response.data["error"]["code"] == "post_not_found"

    def test_comment_content_blank_returns_400(self, api_client, caregiver, elder, post_factory):
        post = post_factory(author=caregiver, text="Post payload inválido", comments_count=0)
        url = reverse("post-comment-create", kwargs={"post_id": post.id})
        api_client.force_authenticate(user=elder)

        response = api_client.post(url, {"content": "   "}, format="json")

        post.refresh_from_db()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False
        assert response.data["error"]["code"] == "VALIDATION_ERROR"
        assert "content" in response.data["error"]["details"]
        assert post.comments_count == 0
        assert PostComment.objects.filter(post=post).count() == 0

    def test_comment_content_too_long_returns_400(self, api_client, caregiver, elder, post_factory):
        post = post_factory(author=caregiver, text="Post payload inválido", comments_count=0)
        url = reverse("post-comment-create", kwargs={"post_id": post.id})
        api_client.force_authenticate(user=elder)
        too_long_content = "a" * 501

        response = api_client.post(url, {"content": too_long_content}, format="json")

        post.refresh_from_db()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False
        assert response.data["error"]["code"] == "VALIDATION_ERROR"
        assert "content" in response.data["error"]["details"]
        assert post.comments_count == 0
        assert PostComment.objects.filter(post=post).count() == 0

    def test_list_comments_requires_authentication(self, api_client, caregiver, post_factory):
        post = post_factory(author=caregiver, text="Post sem auth")
        url = reverse("post-comment-create", kwargs={"post_id": post.id})

        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_list_comments_success_with_cursor_pagination(self, api_client, caregiver, elder, post_factory):
        post = post_factory(author=caregiver, text="Post com muitos comentários", comments_count=25)
        url = reverse("post-comment-create", kwargs={"post_id": post.id})
        api_client.force_authenticate(user=elder)

        for i in range(25):
            PostComment.objects.create(user=elder, post=post, content=f"Comentário {i}")

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "results" in response.data
        assert "next" in response.data
        assert len(response.data["results"]) == 20
        assert response.data["next"] is not None

        next_response = api_client.get(response.data["next"])
        assert next_response.status_code == status.HTTP_200_OK
        assert "results" in next_response.data
        assert len(next_response.data["results"]) == 5

    def test_list_comments_post_not_found_returns_404(self, api_client, elder):
        api_client.force_authenticate(user=elder)
        url = reverse("post-comment-create", kwargs={"post_id": 999999})

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["success"] is False
        assert response.data["error"]["code"] == "post_not_found"

    def test_patch_comment_requires_authentication(self, api_client, caregiver, elder, post_factory):
        post = post_factory(author=caregiver, text="Post sem auth")
        comment = PostComment.objects.create(user=elder, post=post, content="Comentário inicial")
        url = reverse("post-comment-detail", kwargs={"post_id": post.id, "comment_id": comment.id})

        response = api_client.patch(url, {"content": "Atualizado"}, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_delete_comment_requires_authentication(self, api_client, caregiver, elder, post_factory):
        post = post_factory(author=caregiver, text="Post sem auth", comments_count=1)
        comment = PostComment.objects.create(user=elder, post=post, content="Comentário inicial")
        url = reverse("post-comment-detail", kwargs={"post_id": post.id, "comment_id": comment.id})

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_patch_comment_success_for_comment_owner(self, api_client, caregiver, elder, post_factory):
        post = post_factory(author=caregiver, text="Post edição")
        comment = PostComment.objects.create(user=elder, post=post, content="Comentário inicial")
        url = reverse("post-comment-detail", kwargs={"post_id": post.id, "comment_id": comment.id})
        api_client.force_authenticate(user=elder)

        response = api_client.patch(url, {"content": "Comentário atualizado"}, format="json")

        comment.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["data"]["id"] == comment.id
        assert response.data["data"]["content"] == "Comentário atualizado"
        assert comment.content == "Comentário atualizado"

    def test_patch_comment_denied_for_post_owner_when_not_comment_owner(self, api_client, caregiver, elder, post_factory):
        post = post_factory(author=caregiver, text="Post edição")
        comment = PostComment.objects.create(user=elder, post=post, content="Comentário inicial")
        url = reverse("post-comment-detail", kwargs={"post_id": post.id, "comment_id": comment.id})
        api_client.force_authenticate(user=caregiver)

        response = api_client.patch(url, {"content": "Tentativa"}, format="json")

        comment.refresh_from_db()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["success"] is False
        assert response.data["error"]["code"] == "comment_permission_denied"
        assert comment.content == "Comentário inicial"

    def test_patch_comment_success_for_staff(self, api_client, caregiver, elder, post_factory, create_user):
        post = post_factory(author=caregiver, text="Post edição")
        comment = PostComment.objects.create(user=elder, post=post, content="Comentário inicial")
        staff_user = create_user(email="staff_comment_patch@example.com", is_staff=True)
        url = reverse("post-comment-detail", kwargs={"post_id": post.id, "comment_id": comment.id})
        api_client.force_authenticate(user=staff_user)

        response = api_client.patch(url, {"content": "Editado por staff"}, format="json")

        comment.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["data"]["content"] == "Editado por staff"
        assert comment.content == "Editado por staff"

    def test_patch_comment_blank_content_returns_400(self, api_client, caregiver, elder, post_factory):
        post = post_factory(author=caregiver, text="Post edição")
        comment = PostComment.objects.create(user=elder, post=post, content="Comentário inicial")
        url = reverse("post-comment-detail", kwargs={"post_id": post.id, "comment_id": comment.id})
        api_client.force_authenticate(user=elder)

        response = api_client.patch(url, {"content": "   "}, format="json")

        comment.refresh_from_db()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False
        assert response.data["error"]["code"] == "VALIDATION_ERROR"
        assert "content" in response.data["error"]["details"]
        assert comment.content == "Comentário inicial"

    def test_patch_comment_too_long_content_returns_400(self, api_client, caregiver, elder, post_factory):
        post = post_factory(author=caregiver, text="Post edição")
        comment = PostComment.objects.create(user=elder, post=post, content="Comentário inicial")
        url = reverse("post-comment-detail", kwargs={"post_id": post.id, "comment_id": comment.id})
        api_client.force_authenticate(user=elder)

        response = api_client.patch(url, {"content": "a" * 501}, format="json")

        comment.refresh_from_db()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False
        assert response.data["error"]["code"] == "VALIDATION_ERROR"
        assert "content" in response.data["error"]["details"]
        assert comment.content == "Comentário inicial"

    def test_patch_comment_not_found_when_comment_not_in_post(self, api_client, caregiver, elder, post_factory):
        post = post_factory(author=caregiver, text="Post A")
        other_post = post_factory(author=caregiver, text="Post B")
        comment = PostComment.objects.create(user=elder, post=other_post, content="Comentário inicial")
        url = reverse("post-comment-detail", kwargs={"post_id": post.id, "comment_id": comment.id})
        api_client.force_authenticate(user=elder)

        response = api_client.patch(url, {"content": "Novo conteúdo"}, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["success"] is False
        assert response.data["error"]["code"] == "post_comment_not_found"

    def test_patch_comment_post_not_found_returns_404(self, api_client, elder):
        api_client.force_authenticate(user=elder)
        url = reverse("post-comment-detail", kwargs={"post_id": 999999, "comment_id": 1})

        response = api_client.patch(url, {"content": "Novo conteúdo"}, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["success"] is False
        assert response.data["error"]["code"] == "post_not_found"

    def test_delete_comment_success_for_comment_owner(self, api_client, caregiver, elder, post_factory):
        post = post_factory(author=caregiver, text="Post delete", comments_count=1)
        comment = PostComment.objects.create(user=elder, post=post, content="Comentário")
        url = reverse("post-comment-detail", kwargs={"post_id": post.id, "comment_id": comment.id})
        api_client.force_authenticate(user=elder)

        response = api_client.delete(url)

        post.refresh_from_db()
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert post.comments_count == 0
        assert not PostComment.objects.filter(id=comment.id).exists()

    def test_delete_comment_success_for_post_owner(self, api_client, caregiver, elder, post_factory):
        post = post_factory(author=caregiver, text="Post delete", comments_count=1)
        comment = PostComment.objects.create(user=elder, post=post, content="Comentário")
        url = reverse("post-comment-detail", kwargs={"post_id": post.id, "comment_id": comment.id})
        api_client.force_authenticate(user=caregiver)

        response = api_client.delete(url)

        post.refresh_from_db()
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert post.comments_count == 0
        assert not PostComment.objects.filter(id=comment.id).exists()

    def test_delete_comment_success_for_staff(self, api_client, caregiver, elder, post_factory, create_user):
        post = post_factory(author=caregiver, text="Post delete", comments_count=1)
        comment = PostComment.objects.create(user=elder, post=post, content="Comentário")
        staff_user = create_user(email="staff_comment_delete@example.com", is_staff=True)
        url = reverse("post-comment-detail", kwargs={"post_id": post.id, "comment_id": comment.id})
        api_client.force_authenticate(user=staff_user)

        response = api_client.delete(url)

        post.refresh_from_db()
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert post.comments_count == 0
        assert not PostComment.objects.filter(id=comment.id).exists()

    def test_delete_comment_denied_for_third_party(self, api_client, caregiver, elder, other_user, post_factory):
        post = post_factory(author=caregiver, text="Post delete", comments_count=1)
        comment = PostComment.objects.create(user=elder, post=post, content="Comentário")
        url = reverse("post-comment-detail", kwargs={"post_id": post.id, "comment_id": comment.id})
        api_client.force_authenticate(user=other_user)

        response = api_client.delete(url)

        post.refresh_from_db()
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["success"] is False
        assert response.data["error"]["code"] == "comment_permission_denied"
        assert post.comments_count == 1
        assert PostComment.objects.filter(id=comment.id).exists()

    def test_delete_comment_not_found_when_comment_not_in_post(self, api_client, caregiver, elder, post_factory):
        post = post_factory(author=caregiver, text="Post A")
        other_post = post_factory(author=caregiver, text="Post B", comments_count=1)
        comment = PostComment.objects.create(user=elder, post=other_post, content="Comentário inicial")
        url = reverse("post-comment-detail", kwargs={"post_id": post.id, "comment_id": comment.id})
        api_client.force_authenticate(user=elder)

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["success"] is False
        assert response.data["error"]["code"] == "post_comment_not_found"

    def test_delete_comment_post_not_found_returns_404(self, api_client, elder):
        api_client.force_authenticate(user=elder)
        url = reverse("post-comment-detail", kwargs={"post_id": 999999, "comment_id": 1})

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["success"] is False
        assert response.data["error"]["code"] == "post_not_found"
