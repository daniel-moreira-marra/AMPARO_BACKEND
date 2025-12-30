from django.db import models

from accounts.models.caregiver_profile import CaregiverProfile

class CareType(models.TextChoices):
    HOME = "HOME", "Domiciliar"
    HOSPITAL = "HOSPITAL", "Hospitalar"
    NIGHT_SHIFT = "NIGHT_SHIFT", "Plantão noturno"
    DAY_SHIFT = "DAY_SHIFT", "Plantão diurno"
    COMPANION = "COMPANION", "Acompanhante"


class CaregiverCareType(models.Model):
    """
    Associação entre Caregiver e tipos de cuidado.
    """

    caregiver = models.ForeignKey(
        CaregiverProfile,
        on_delete=models.CASCADE,
        related_name="care_types",
    )

    care_type = models.CharField(
        max_length=20,
        choices=CareType.choices,
        default=CareType.HOME,
    )

    hourly_rate = models.DecimalField(
        "valor por hora",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Se preferir, você pode modelar preço em outra tabela futuramente.",
    )

    class Meta:
        unique_together = ("caregiver", "care_type")
        verbose_name = "Tipo de cuidado do cuidador"
        verbose_name_plural = "Tipos de cuidado do cuidador"

    def __str__(self) -> str:
        return f"{self.caregiver.user.email} - {self.care_type}"

