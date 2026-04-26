from django.db import models


class GuardianElderLink(models.Model):
    class Relationship(models.TextChoices):
        CHILD = "CHILD", "Filho(a)"
        SPOUSE = "SPOUSE", "Cônjuge"
        RELATIVE = "RELATIVE", "Parente"
        LEGAL_GUARDIAN = "LEGAL_GUARDIAN", "Responsável legal"
        OTHER = "OTHER", "Outro"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pendente"
        ACTIVE = "ACTIVE", "Ativo"
        ENDED = "ENDED", "Finalizado"
        CANCELLED = "CANCELLED", "Cancelado"

    guardian = models.ForeignKey(
        "accounts.GuardianProfile",
        on_delete=models.CASCADE,
        related_name="elder_links",
    )
    elder = models.ForeignKey(
        "accounts.ElderProfile",
        on_delete=models.CASCADE,
        related_name="guardian_links",
    )

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    relationship = models.CharField(max_length=30, choices=Relationship.choices, default=Relationship.OTHER)
    is_legal_guardian = models.BooleanField(default=False)

    can_view_medical = models.BooleanField(default=True)
    can_hire = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("guardian", "elder")
        indexes = [
            models.Index(fields=["elder", "status"]),
            models.Index(fields=["guardian", "status"]),
        ]
