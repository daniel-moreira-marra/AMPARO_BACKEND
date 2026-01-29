from django.db import models

from ..enums.enums import ServiceMode

class ProfessionalElderLink(models.Model):
    """
    Vínculo (contrato/atendimento) entre um profissional e um idoso.

    Serve para:
    - histórico de atendimentos
    - status do vínculo
    - período de acompanhamento
    - preço acordado (snapshot)
    - modalidade do serviço
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pendente"
        ACTIVE = "ACTIVE", "Ativo"
        ENDED = "ENDED", "Finalizado"
        CANCELLED = "CANCELLED", "Cancelado"

    elder = models.ForeignKey(
        "accounts.ElderProfile",
        on_delete=models.CASCADE,
        related_name="professional_links",
    )
    professional = models.ForeignKey(
        "accounts.ProfessionalProfile",
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

    # Modalidade no vínculo (pode diferir do perfil)
    service_mode = models.CharField(
        "modalidade",
        max_length=20,
        blank=True,
        choices=ServiceMode.choices,
        help_text="Ex.: HOME, CLINIC, ONLINE. Pode ser alinhado ao enum do ProfessionalProfile futuramente.",
    )

    goals = models.TextField(
        "objetivos do acompanhamento",
        blank=True,
        help_text="Ex.: reabilitação pós-cirurgia, ganho de mobilidade, etc.",
    )
    notes = models.TextField("observações", blank=True)

    is_active = models.BooleanField("vínculo ativo", default=True)

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Vínculo idoso-profissional"
        verbose_name_plural = "Vínculos idoso-profissional"
        indexes = [
            models.Index(fields=["elder", "is_active"]),
            models.Index(fields=["professional", "is_active"]),
            models.Index(fields=["status"]),
        ]
        constraints = [
            # Evita dois vínculos ativos para o mesmo par (permite histórico)
            models.UniqueConstraint(
                fields=["elder", "professional"],
                condition=models.Q(is_active=True),
                name="uniq_active_elder_professional_link",
            )
        ]

    def __str__(self) -> str:
        return f"{self.elder.user.email} ↔ {self.professional.user.email} ({self.status})"
