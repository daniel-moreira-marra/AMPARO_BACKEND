import pytest
from django.urls import reverse
from rest_framework import status
from posts.enums import VisibilityScope

@pytest.mark.django_db
@pytest.mark.integration
class TestPostResponseContract:
    """
    Testa se a API respeita o contrato {success, data} ou {success, error}.
    """

    def test_success_response_format(self, api_client, caregiver):
        api_client.force_authenticate(user=caregiver)
        url = reverse("my-posts-list-create")
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert "success" in response.data
        assert response.data["success"] is True
        assert "data" in response.data

    def test_error_response_format(self, api_client):
        # Tentativa de listar sem autenticação deve retornar erro formatado (se houver middleware/handler)
        # Se o handler customizado estiver ativo, deve seguir o padrão.
        url = reverse("my-posts-list-create")
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "success" in response.data
        assert response.data["success"] is False
        assert "error" in response.data
        assert "code" in response.data["error"]
        assert "message" in response.data["error"]

@pytest.mark.django_db
@pytest.mark.permissions
class TestPostPermissions:
    """
    Testa permissões de CRUD de posts.
    """

    def test_cannot_list_other_users_posts(self, api_client, caregiver, other_user, post_factory):
        # Post do other_user
        post_factory(author=other_user, text="Post do Outro")
        
        api_client.force_authenticate(user=caregiver)
        url = reverse("my-posts-list-create")
        
        response = api_client.get(url)
        
        # O MyPostsViewSet filtra pelo autor, então o post do other_user não deve aparecer
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 0

    def test_cannot_edit_other_users_post(self, api_client, caregiver, other_user, post_factory):
        post = post_factory(author=other_user, text="Original")
        
        api_client.force_authenticate(user=caregiver)
        # Tenta acessar o detalhe do post de outro via MyPosts (deve dar 404 por causa do queryset filter)
        url = reverse("my-posts-detail", kwargs={"pk": post.pk})
        
        response = api_client.patch(url, {"text": "Hackeado"})
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_owner_can_edit_own_post(self, api_client, caregiver, post_factory):
        post = post_factory(author=caregiver, text="Original")
        
        api_client.force_authenticate(user=caregiver)
        url = reverse("my-posts-detail", kwargs={"pk": post.pk})
        
        response = api_client.patch(url, {"text": "Editado"})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["text"] == "Editado"
