from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from ..enums import UserRole


class UserManager(BaseUserManager):
    """
    Manager para criar usuários usando e-mail como identificador.
    """

    def create_user(self, email: str, password: str | None = None, **extra_fields):
        if not email:
            raise ValueError("O e-mail é obrigatório.")
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # hash seguro
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser precisa ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser precisa ter is_superuser=True.")

        return self.create_user(email=email, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=30, blank=True)
    address_line = models.CharField("endereço", max_length=255, blank=True)
    city = models.CharField("cidade", max_length=120, blank=True)
    state = models.CharField("estado", max_length=2, blank=True)
    zip_code = models.CharField("CEP", max_length=8, blank=True)

    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    role = models.CharField(max_length=20, choices=UserRole.choices)

    show_email = models.BooleanField("compartilhar e-mail", default=False)
    show_phone = models.BooleanField("compartilhar telefone", default=False)
    show_links = models.BooleanField("compartilhar vínculos", default=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    onboarding_completed = models.BooleanField("onboarding completo", default=False)

    objects = UserManager()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    def __str__(self):
        return self.email
