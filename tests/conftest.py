import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from accounts.models.caregiver_profile import CaregiverProfile
from accounts.models.elder_profile import ElderProfile
from accounts.models.caregiver_elder_link import CaregiverElderLink
from posts.models.posts import Post
from posts.enums import VisibilityScope, PostStatus
from accounts.enums import UserRole

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user(db):
    def _create_user(email="test@example.com", password="password123", role="ELDER", full_name="Test User", **extra_fields):
        # Garante que o email seja único se não for passado
        import uuid
        if email == "test@example.com":
             email = f"test_{uuid.uuid4().hex[:8]}@example.com"
             
        user = User.objects.create_user(
            email=email, 
            password=password, 
            role=role, 
            full_name=full_name, 
            **extra_fields
        )
        return user
    return _create_user

@pytest.fixture
def create_post(db):
    def _create_post(author, text="Conteúdo do post", visibility_scope=VisibilityScope.PUBLIC, status=PostStatus.PUBLISHED, **extra_fields):
        # Traduz visibility -> visibility_scope se necessário (para compatibilidade)
        if "visibility" in extra_fields:
            visibility_scope = extra_fields.pop("visibility")
            
        return Post.objects.create(
            author=author,
            text=text,
            visibility_scope=visibility_scope,
            status=status,
            **extra_fields
        )
    return _create_post

@pytest.fixture
def auth_client(api_client, create_user):
    def _auth_client(email, password="password123", role="ELDER"):
        user, created = User.objects.get_or_create(
            email=email, 
            defaults={"role": role, "full_name": "Auth User"}
        )
        if not created and not user.check_password(password):
            user.set_password(password)
            user.save()
        api_client.force_authenticate(user=user)
        return api_client
    return _auth_client

# --- Aliases para compatibilidade com meus novos testes ---

@pytest.fixture
def user_factory(create_user):
    return create_user

@pytest.fixture
def post_factory(create_post):
    return create_post

# --- Novas fixtures de domínio ---

@pytest.fixture
def caregiver(create_user):
    user = create_user(email="caregiver@amparo.com", role=UserRole.CAREGIVER)
    CaregiverProfile.objects.get_or_create(user=user)
    return user

@pytest.fixture
def elder(create_user):
    user = create_user(email="elder@amparo.com", role=UserRole.ELDER)
    ElderProfile.objects.get_or_create(user=user)
    return user

@pytest.fixture
def other_user(create_user):
    return create_user(email="other@amparo.com", role=UserRole.ELDER)

@pytest.fixture
def active_link(caregiver, elder):
    return CaregiverElderLink.objects.create(
        caregiver=caregiver.caregiver_profile,
        elder=elder.elder_profile,
        status=CaregiverElderLink.Status.ACTIVE,
        is_active=True
    )
