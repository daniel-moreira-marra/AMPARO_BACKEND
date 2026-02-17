from django.db import models
from accounts.enums.enums import CareType


class CaregiverElderLinkCareType(models.Model):
    """
    Tipos de cuidado associados a um vínculo CaregiverElderLink.
    Mantém TextChoices e permite múltiplos care types por contrato.
    """

    link = models.ForeignKey(
        "links.CaregiverElderLink",
        on_delete=models.CASCADE,
        related_name="care_types",
    )

    care_type = models.CharField(max_length=20, choices=CareType.choices)

    class Meta:
        verbose_name = "Tipo de cuidado do vínculo"
        verbose_name_plural = "Tipo de cuidado do vínculo"
        constraints = [
            models.UniqueConstraint(
                fields=["link", "care_type"],
                name="uniq_link_care_type_links",
            )
        ]

    def __str__(self) -> str:
        return f"{self.link_id} - {self.care_type}"
