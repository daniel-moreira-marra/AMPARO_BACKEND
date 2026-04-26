from django.conf import settings
from django.db import models

from ..enums.enums import ServiceMode

class ProfessionalProfile(models.Model):
    """
    Perfil do PROFISSIONAL (PROFESSIONAL), ex.: fisioterapeuta, fonoaudiólogo etc.
    """

    class Profession(models.TextChoices):
        PHYSIOTHERAPIST = "PHYSIOTHERAPIST", "Fisioterapeuta"
        SPEECH_THERAPIST = "SPEECH_THERAPIST", "Fonoaudiólogo(a)"
        OCCUPATIONAL_THERAPIST = "OCCUPATIONAL_THERAPIST", "Terapeuta ocupacional"
        PSYCHOLOGIST = "PSYCHOLOGIST", "Psicólogo(a)"
        NUTRITIONIST = "NUTRITIONIST", "Nutricionista"
        OTHER = "OTHER", "Outro"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="professional_profile",
    )

    profession = models.CharField("profissão", max_length=30, choices=Profession.choices)
    profession_other = models.CharField("especialidade (outro)", max_length=100, blank=True)
    council = models.CharField(
        "conselho profissional",
        max_length=20,
        blank=True,
        help_text="Ex.: CREFITO, CRP, CRM, etc.",
    )
    license_number = models.CharField("registro profissional", max_length=50, blank=True)

    bio = models.TextField("biografia", blank=True)
    service_mode = models.CharField("modalidade", max_length=20, choices=ServiceMode.choices, default=ServiceMode.HOME)

    hourly_rate = models.DecimalField("valor por hora", max_digits=10, decimal_places=2, null=True, blank=True)

    is_available = models.BooleanField("disponível para contratação", default=True)
    registration_verified = models.BooleanField("registro verificado", default=False)

    city = models.CharField("cidade", max_length=120, blank=True)
    state = models.CharField("estado", max_length=2, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"ProfessionalProfile<{self.user.email}>"
