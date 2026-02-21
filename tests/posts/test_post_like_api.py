import pytest
from django.urls import reverse
from rest_framework import status

from posts.models import PostLike


@pytest.mark.django_db
class TestPostLikeAPI:
    def test_like_requires_authentication(self, api_client, caregiver, post_factory):
        post = post_factory(author=caregiver, text="Post sem auth")
        url = reverse("post-like-create", kwargs={"post_id": post.id})

        response = api_client.post(url, {})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_like_post_success(self, api_client, caregiver, elder, post_factory):
        post = post_factory(author=caregiver, text="Post para like")
        url = reverse("post-like-create", kwargs={"post_id": post.id})
        api_client.force_authenticate(user=elder)

        response = api_client.post(url, {})

        post.refresh_from_db()
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True
        assert response.data["data"]["post_id"] == post.id
        assert response.data["data"]["user_id"] == elder.id
        assert response.data["data"]["likes_count"] == 1
        assert post.likes_count == 1
        assert PostLike.objects.filter(user=elder, post=post).exists()

    def test_like_post_duplicate_returns_conflict(self, api_client, caregiver, elder, post_factory):
        post = post_factory(author=caregiver, text="Post duplicado")
        url = reverse("post-like-create", kwargs={"post_id": post.id})
        api_client.force_authenticate(user=elder)

        first_response = api_client.post(url, {})
        second_response = api_client.post(url, {})

        post.refresh_from_db()
        assert first_response.status_code == status.HTTP_201_CREATED
        assert second_response.status_code == status.HTTP_409_CONFLICT
        assert second_response.data["success"] is False
        assert second_response.data["error"]["code"] == "post_already_liked"
        assert post.likes_count == 1
        assert PostLike.objects.filter(user=elder, post=post).count() == 1

    def test_like_post_not_found_returns_404(self, api_client, elder):
        api_client.force_authenticate(user=elder)
        url = reverse("post-like-create", kwargs={"post_id": 999999})

        response = api_client.post(url, {})

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["success"] is False
        assert response.data["error"]["code"] == "post_not_found"


@pytest.mark.django_db
class TestPostUnlikeAPI:
    def test_unlike_requires_authentication(self, api_client, caregiver, elder, post_factory):
        post = post_factory(author=caregiver, text="Post unlike sem auth", likes_count=1)
        PostLike.objects.create(user=elder, post=post)
        url = reverse("post-unlike", kwargs={"post_id": post.id})

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_unlike_post_success_returns_204(self, api_client, caregiver, elder, post_factory):
        post = post_factory(author=caregiver, text="Post unlike", likes_count=1)
        PostLike.objects.create(user=elder, post=post)
        api_client.force_authenticate(user=elder)
        url = reverse("post-unlike", kwargs={"post_id": post.id})

        response = api_client.delete(url)

        post.refresh_from_db()
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.content in (b"", None)
        assert post.likes_count == 0
        assert not PostLike.objects.filter(user=elder, post=post).exists()

    def test_unlike_post_missing_like_returns_404(self, api_client, caregiver, elder, post_factory):
        post = post_factory(author=caregiver, text="Sem like para remover", likes_count=0)
        api_client.force_authenticate(user=elder)
        url = reverse("post-unlike", kwargs={"post_id": post.id})

        response = api_client.delete(url)

        post.refresh_from_db()
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["success"] is False
        assert response.data["error"]["code"] == "post_like_not_found"
        assert post.likes_count == 0

    def test_unlike_post_not_found_returns_404(self, api_client, elder):
        api_client.force_authenticate(user=elder)
        url = reverse("post-unlike", kwargs={"post_id": 999999})

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.data["success"] is False
        assert response.data["error"]["code"] == "post_not_found"

    def test_unlike_repeated_call_returns_404_and_keeps_counter(self, api_client, caregiver, elder, post_factory):
        post = post_factory(author=caregiver, text="Unlike repetido", likes_count=1)
        PostLike.objects.create(user=elder, post=post)
        api_client.force_authenticate(user=elder)
        url = reverse("post-unlike", kwargs={"post_id": post.id})

        first_response = api_client.delete(url)
        second_response = api_client.delete(url)

        post.refresh_from_db()
        assert first_response.status_code == status.HTTP_204_NO_CONTENT
        assert second_response.status_code == status.HTTP_404_NOT_FOUND
        assert second_response.data["success"] is False
        assert second_response.data["error"]["code"] == "post_like_not_found"
        assert post.likes_count == 0
