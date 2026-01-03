from django.db import models


class CaregiverElderLink(models.Model):
    """
    Vínculo (contrato/atendimento) entre um cuidador e um idoso.

    Use para:
    - histórico de atendimentos
    - status do vínculo
    - preço acordado (snapshot)
    - período do atendimento
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pendente"
        ACTIVE = "ACTIVE", "Ativo"
        ENDED = "ENDED", "Finalizado"
        CANCELLED = "CANCELLED", "Cancelado"

    elder = models.ForeignKey(
        "accounts.ElderProfile",
        on_delete=models.CASCADE,
        related_name="caregiver_links",
    )
    caregiver = models.ForeignKey(
        "accounts.CaregiverProfile",
        on_delete=models.CASCADE,
        related_name="elder_links",
    )

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)

    started_at = models.DateField("início", null=True, blank=True)
    ended_at = models.DateField("fim", null=True, blank=True)

    agreed_hourly_rate = models.DecimalField(
        "valor/hora acordado",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Snapshot do valor combinado no vínculo (pode diferir do perfil).",
    )

    notes = models.TextField("observações", blank=True)
    is_active = models.BooleanField("vínculo ativo", default=True)

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Vínculo idoso-cuidador"
        verbose_name_plural = "Vínculos idoso-cuidador"
        indexes = [
            models.Index(fields=["elder", "is_active"]),
            models.Index(fields=["caregiver", "is_active"]),
            models.Index(fields=["status"]),
        ]
        constraints = [
            # Evita dois vínculos ativos para o mesmo par (permite histórico)
            models.UniqueConstraint(
                fields=["elder", "caregiver"],
                condition=models.Q(is_active=True),
                name="uniq_active_elder_caregiver_link",
            )
        ]

    def __str__(self) -> str:
        return f"{self.elder.user.email} ↔ {self.caregiver.user.email} ({self.status})"
