import pytest
from django.core.cache import cache
from posts.services.post_services import create_post as create_post_service, delete_post as delete_post_service
from posts.enums import PostStatus, VisibilityScope

@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()

@pytest.mark.django_db
def test_feed_cache_hit_and_miss(auth_client, create_post):
    from accounts.models import User
    user_client = auth_client(email="hitmiss@test.com", role="ELDER")
    user = User.objects.get(email="hitmiss@test.com")
    
    # Criar posts publicados com o mesmo autor
    create_post(author=user, text="Post 1", status=PostStatus.PUBLISHED, visibility_scope=VisibilityScope.PUBLIC)
    create_post(author=user, text="Post 2", status=PostStatus.PUBLISHED, visibility_scope=VisibilityScope.PUBLIC)
    
    url = "/api/v1/posts/feed/"
    
    # Primeira chamada: MISS
    resp1 = user_client.get(url)
    assert resp1.status_code == 200
    assert resp1["X-Cache"] == "MISS"
    
    # Segunda chamada: HIT
    resp2 = user_client.get(url)
    assert resp2.status_code == 200
    assert resp2["X-Cache"] == "HIT"

@pytest.mark.django_db
def test_feed_cache_invalidation_on_create(auth_client, create_post):
    from accounts.models import User
    user_client = auth_client(email="inv_create@test.com", role="ELDER")
    user = User.objects.get(email="inv_create@test.com")
    
    create_post(author=user, text="Post 1", status=PostStatus.PUBLISHED, visibility_scope=VisibilityScope.PUBLIC)
    
    url = "/api/v1/posts/feed/"
    
    # Cache miss inicial
    user_client.get(url)
    # Cache hit
    resp2 = user_client.get(url)
    assert resp2["X-Cache"] == "HIT"
    
    # Criar novo post via service (deve invalidar)
    create_post_service(
        actor=user,
        data={"text": "Novo Post", "visibility_scope": VisibilityScope.PUBLIC}
    )
    
    # Deve ser MISS novamente
    resp3 = user_client.get(url)
    assert resp3["X-Cache"] == "MISS"

@pytest.mark.django_db
def test_feed_cache_invalidation_on_delete(auth_client, create_post):
    from accounts.models import User
    user_client = auth_client(email="inv_delete@test.com", role="ELDER")
    user = User.objects.get(email="inv_delete@test.com")
    
    post = create_post(author=user, text="Post 1", status=PostStatus.PUBLISHED, visibility_scope=VisibilityScope.PUBLIC)
    
    url = "/api/v1/posts/feed/"
    
    # Alimentar cache
    user_client.get(url)
    resp_hit = user_client.get(url)
    assert resp_hit["X-Cache"] == "HIT"
    
    # Deletar post via service
    delete_post_service(actor=user, post_id=post.id)
    
    # Deve ser MISS
    resp_miss = user_client.get(url)
    assert resp_miss["X-Cache"] == "MISS"

@pytest.mark.django_db
def test_feed_cache_user_isolation(api_client, create_user, create_post):
    from rest_framework_simplejwt.tokens import AccessToken
    
    user_a = create_user(email="user_a@test.com", role="ELDER")
    user_b = create_user(email="user_b@test.com", role="ELDER")
    
    create_post(author=user_a, text="Public Post", status=PostStatus.PUBLISHED, visibility_scope=VisibilityScope.PUBLIC)
    
    url = "/api/v1/posts/feed/"
    
    # Client A
    client_a = api_client
    client_a.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(user_a)}")
    resp_a = client_a.get(url)
    assert resp_a["X-Cache"] == "MISS"
    
    # Client B (Novo Objeto para garantir isolamento no teste)
    from rest_framework.test import APIClient
    client_b = APIClient()
    client_b.credentials(HTTP_AUTHORIZATION=f"Bearer {AccessToken.for_user(user_b)}")
    resp_b = client_b.get(url)
    
    assert resp_b["X-Cache"] == "MISS"
