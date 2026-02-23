from django.conf import settings
from django.db import models


class InstitutionProfile(models.Model):
    """
    Perfil da INSTITUIÇÃO (INSTITUTION).

    Armazena dados institucionais (CNPJ, capacidade, tipo, endereço).
    """

    class InstitutionType(models.TextChoices):
        ILPI = "ILPI", "ILPI (Longa Permanência)"
        SHELTER = "SHELTER", "Abrigo"
        CLINIC = "CLINIC", "Clínica"
        HOSPITAL = "HOSPITAL", "Hospital"
        OTHER = "OTHER", "Outro"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="institution_profile",
    )

    legal_name = models.CharField("razão social", max_length=255)
    trade_name = models.CharField("nome fantasia", max_length=255, blank=True)

    cnpj = models.CharField(
        "CNPJ",
        max_length=14,
        blank=True,
        help_text="Armazene apenas números. Validação pode ser adicionada no serializer.",
    )

    institution_type = models.CharField(
        "tipo",
        max_length=20,
        choices=InstitutionType.choices,
        default=InstitutionType.OTHER,
    )

    capacity = models.PositiveIntegerField("capacidade", null=True, blank=True)
    website = models.URLField("site", blank=True)

    # Compliance / licenças (se existir)
    license_number = models.CharField("nº licença/alvará", max_length=80, blank=True)
    is_verified = models.BooleanField("instituição verificada", default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"InstitutionProfile<{self.legal_name}>"
