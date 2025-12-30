from django.conf import settings
from django.db import models


class CaregiverProfile(models.Model):
    """
    Perfil do CUIDADOR (CAREGIVER).

    Mantém dados profissionais e operacionais para matching/contratação.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="caregiver_profile",
    )

    bio = models.TextField("biografia", blank=True)
    experience_years = models.PositiveSmallIntegerField("anos de experiência", default=0)

    is_available = models.BooleanField("disponível para contratação", default=True)

    # Verificações (boas para trust & safety)
    background_check_status = models.CharField("status de verificação", max_length=30, blank=True)
    documents_verified = models.BooleanField("documentos verificados", default=False)

    # Localização simples (pode evoluir para endereços ou geolocalização)
    city = models.CharField("cidade", max_length=120, blank=True)
    state = models.CharField("estado", max_length=2, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"CaregiverProfile<{self.user.email}>"
