from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin


class UserRole(models.TextChoices):
    ELDER = "ELDER", "Idoso"
    GUARDIAN = "GUARDIAN", "Responsável"
    CAREGIVER = "CAREGIVER", "Cuidador"
    INSTITUTION = "INSTITUTION", "Instituição"
    PROFESSIONAL = "PROFESSIONAL", "Profissional de saúde" 

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

    role = models.CharField(max_length=20, choices=UserRole.choices)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    objects = UserManager()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    def __str__(self):
        return self.email
