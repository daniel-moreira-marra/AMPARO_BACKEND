from django.db import models


class InstitutionElderLink(models.Model):
    """
    Vínculo entre um idoso e uma instituição.

    Serve para:
    - histórico de permanência
    - status atual (ativo/inativo)
    - dados específicos do vínculo (quarto/leito, plano, observações)
    """

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Ativo"
        DISCHARGED = "DISCHARGED", "Alta/saída"
        TRANSFERRED = "TRANSFERRED", "Transferido"
        CANCELLED = "CANCELLED", "Cancelado"
        OTHER = "OTHER", "Outro"

    elder = models.ForeignKey(
        "accounts.ElderProfile",
        on_delete=models.CASCADE,
        related_name="institution_links",
    )
    institution = models.ForeignKey(
        "accounts.InstitutionProfile",
        on_delete=models.CASCADE,
        related_name="elder_links",
    )

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    admitted_at = models.DateField("data de admissão", null=True, blank=True)
    discharged_at = models.DateField("data de saída", null=True, blank=True)

    # Campos úteis, mas opcionais (podem evoluir depois)
    room = models.CharField("quarto", max_length=30, blank=True)
    bed = models.CharField("leito", max_length=30, blank=True)

    notes = models.TextField("observações do vínculo", blank=True)

    is_active = models.BooleanField("vínculo ativo", default=True)

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Vínculo idoso-instituição"
        verbose_name_plural = "Vínculos idoso-instituição"
        indexes = [
            models.Index(fields=["elder", "institution"]),
            models.Index(fields=["institution", "is_active"]),
            models.Index(fields=["elder", "is_active"]),
        ]
        constraints = [
            # Evita duplicar vínculo ativo para o mesmo par
            models.UniqueConstraint(
                fields=["elder", "institution"],
                condition=models.Q(is_active=True),
                name="uniq_active_elder_institution_link",
            )
        ]

    def __str__(self) -> str:
        return f"{self.elder.user.email} ↔ {self.institution.legal_name} ({self.status})"
