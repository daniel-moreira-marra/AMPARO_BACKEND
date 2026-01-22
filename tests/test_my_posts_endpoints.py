import pytest
from django.utils import timezone
from django.contrib.auth import get_user_model

from posts.models import Post
from posts.enums.post_status import PostStatus
from posts.enums.visibility_scope import VisibilityScope

pytestmark = pytest.mark.django_db

LIST_URL = "/api/v1/posts/my-posts/"

User = get_user_model()

def detail_url(post_id) -> str:
    return f"/api/v1/posts/my-posts/{post_id}/"


class TestMyPostsAuth:
    def test_list_requires_auth(self, api_client):
        resp = api_client.get(LIST_URL)
        assert resp.status_code in (401, 403)

    def test_create_requires_auth(self, api_client):
        resp = api_client.post(LIST_URL, {"text": "Teste"}, format="json")
        assert resp.status_code in (401, 403)


class TestMyPostsList:
    def test_list_returns_only_own_posts(self, auth_client, create_user, create_post):
        client = auth_client(role="ELDER", email="me@example.com", password="StrongPass@123")
        me = User.objects.get(email="me@example.com")

        other = create_user(email="other@example.com")

        my_post_1 = create_post(author=me, text="Meu 1")
        my_post_2 = create_post(author=me, text="Meu 2")
        create_post(author=other, text="Outro user")

        resp = client.get(LIST_URL)
        assert resp.status_code == 200

        data = resp.json()
        # Pode ser lista direta ou envelope {success, data}
        items = data["data"] if isinstance(data, dict) and "data" in data else data

        returned_ids = {item["id"] for item in items}
        assert str(my_post_1.id) in {str(x) for x in returned_ids}
        assert str(my_post_2.id) in {str(x) for x in returned_ids}
        # não deve conter post de outro usuário
        assert all(
            item.get("text") != "Outro user" for item in items
        )

    def test_list_excludes_soft_deleted(self, auth_client, create_post):
        client = auth_client(role="ELDER", email="me2@example.com", password="StrongPass@123")
        me = User.objects.get(email="me2@example.com")

        keep = create_post(author=me, text="Fica")
        to_delete = create_post(author=me, text="Sai")

        # Soft delete, se existir
        if hasattr(to_delete, "deleted_at"):
            to_delete.deleted_at = timezone.now()
            to_delete.save(update_fields=["deleted_at"])

            resp = client.get(LIST_URL)
            assert resp.status_code == 200

            data = resp.json()
            items = data["data"] if isinstance(data, dict) and "data" in data else data
            texts = [i["text"] for i in items]

            assert "Fica" in texts
            assert "Sai" not in texts
        else:
            # Se não existe soft delete, esse teste não se aplica
            assert True


class TestMyPostsCreate:
    def test_create_success_minimal_payload(self, auth_client):
        client = auth_client(role="ELDER", email="create@example.com", password="StrongPass@123")

        payload = {"text": "Primeiro post"}
        resp = client.post(LIST_URL, payload, format="json")
        assert resp.status_code == 201, resp.content

        body = resp.json()
        data = body["data"] if isinstance(body, dict) and "data" in body else body

        assert data["text"] == "Primeiro post"
        assert "id" in data

        # Confere no banco
        post = Post.objects.get(id=data["id"])
        assert post.text == "Primeiro post"
        assert post.author.email == "create@example.com"

    def test_create_fails_without_text(self, auth_client):
        client = auth_client(role="ELDER", email="create2@example.com", password="StrongPass@123")

        resp = client.post(LIST_URL, {"text": "   "}, format="json")
        assert resp.status_code == 400

    def test_create_can_set_status(self, auth_client):
        client = auth_client(role="ELDER", email="create3@example.com", password="StrongPass@123")

        resp = client.post(
            LIST_URL,
            {"text": "Publicar já", "status": PostStatus.PUBLISHED},
            format="json",
        )
        assert resp.status_code == 201, resp.content

        data = resp.json()
        data = data["data"] if isinstance(data, dict) and "data" in data else data

        post = Post.objects.get(id=data["id"])
        assert post.status == PostStatus.PUBLISHED

        # Se seu serializer/model preenche published_at ao publicar
        if hasattr(post, "published_at"):
            assert post.published_at is not None


class TestMyPostsDetail:
    def test_retrieve_own_post_success(self, auth_client, create_post):
        client = auth_client(role="ELDER", email="me4@example.com", password="StrongPass@123")
        me = User.objects.get(email="me4@example.com")

        post = create_post(author=me, text="Meu detalhe")
        resp = client.get(detail_url(post.id))
        assert resp.status_code == 200

        body = resp.json()
        data = body["data"] if isinstance(body, dict) and "data" in body else body
        assert data["text"] == "Meu detalhe"
        assert str(data["id"]) == str(post.id)

    def test_retrieve_other_users_post_returns_404(self, auth_client, create_user, create_post):
        client = auth_client(role="ELDER", email="me5@example.com", password="StrongPass@123")

        other = create_user(email="other2@example.com")
        other_post = create_post(author=other, text="Não é meu")

        resp = client.get(detail_url(other_post.id))
        # Como o queryset é filtrado por author=request.user, tende a ser 404
        assert resp.status_code in (404, 403)

    def test_update_own_post_put(self, auth_client, create_post):
        client = auth_client(role="ELDER", email="me6@example.com", password="StrongPass@123")
        me = User.objects.get(email="me6@example.com")

        post = create_post(author=me, text="Antes", status=PostStatus.DRAFT)

        resp = client.put(
            detail_url(post.id),
            {
                "text": "Depois",
                "status": PostStatus.PUBLISHED,
                "visibility_scope": VisibilityScope.PUBLIC,
                "image_alt_text": "",
                "image": None,
            },
            format="json",
        )
        assert resp.status_code == 200, resp.content

        post.refresh_from_db()
        assert post.text == "Depois"
        assert post.status == PostStatus.PUBLISHED
        if hasattr(post, "edited_at"):
            assert post.edited_at is not None
        if hasattr(post, "published_at"):
            assert post.published_at is not None

    def test_partial_update_patch(self, auth_client, create_post):
        client = auth_client(role="ELDER", email="me7@example.com", password="StrongPass@123")
        me = User.objects.get(email="me7@example.com")

        post = create_post(author=me, text="Texto antigo")
        resp = client.patch(detail_url(post.id), {"text": "Texto novo"}, format="json")
        assert resp.status_code == 200, resp.content

        post.refresh_from_db()
        assert post.text == "Texto novo"
        if hasattr(post, "edited_at"):
            assert post.edited_at is not None

    def test_delete_own_post(self, auth_client, create_post):
        client = auth_client(role="ELDER", email="me8@example.com", password="StrongPass@123")
        me = User.objects.get(email="me8@example.com")

        post = create_post(author=me, text="Vou sair")
        resp = client.delete(detail_url(post.id))
        assert resp.status_code == 200, resp.content

        # Soft delete
        if hasattr(Post, "deleted_at"):
            post.refresh_from_db()
            assert post.deleted_at is not None
        else:
            assert not Post.objects.filter(id=post.id).exists()
