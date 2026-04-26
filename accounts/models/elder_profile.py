from django.conf import settings
from django.db import models


class ElderProfile(models.Model):
    """
    Dados específicos do idoso.

    Mantém informações úteis para:
    - busca/matching de cuidadores e instituições
    - segurança (contato de emergência)
    - expansão futura
    """

    class Gender(models.TextChoices):
        MALE = "MALE", "Masculino"
        FEMALE = "FEMALE", "Feminino"
        OTHER = "OTHER", "Outro"
        NOT_INFORMED = "NOT_INFORMED", "Não informado"

    class MobilityLevel(models.TextChoices):
        INDEPENDENT = "INDEPENDENT", "Independente"
        NEEDS_ASSISTANCE = "NEEDS_ASSISTANCE", "Precisa de ajuda"
        WHEELCHAIR = "WHEELCHAIR", "Cadeira de rodas"
        BEDRIDDEN = "BEDRIDDEN", "Acamado(a)"

    class CognitiveStatus(models.TextChoices):
        LUCID = "LUCID", "Lúcido(a)"
        MILD_IMPAIRMENT = "MILD_IMPAIRMENT", "Comprometimento leve"
        DEMENTIA = "DEMENTIA", "Demência"
        NOT_INFORMED = "NOT_INFORMED", "Não informado"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="elder_profile",
    )

    preferred_name = models.CharField("nome social/preferido", max_length=150, blank=True)
    birth_date = models.DateField("data de nascimento", null=True, blank=True)
    gender = models.CharField("gênero", max_length=20, choices=Gender.choices, default=Gender.NOT_INFORMED)

    mobility_level = models.CharField(
        "mobilidade",
        max_length=20,
        choices=MobilityLevel.choices,
        default=MobilityLevel.INDEPENDENT,
    )
    cognitive_status = models.CharField(
        "condição cognitiva",
        max_length=30,
        choices=CognitiveStatus.choices,
        default=CognitiveStatus.NOT_INFORMED,
    )



    has_fall_risk = models.BooleanField("risco de quedas", default=False)
    needs_medication_support = models.BooleanField("precisa de ajuda com medicação", default=False)
    requires_24h_care = models.BooleanField("necessita cuidado 24h", default=False)

    medical_conditions = models.TextField("condições médicas", blank=True)
    allergies = models.TextField("alergias", blank=True)
    medications = models.TextField("medicações", blank=True)
    medical_notes = models.TextField("observações médicas", blank=True)

    emergency_contact_name = models.CharField("contato de emergência - nome", max_length=150, blank=True)
    emergency_contact_phone = models.CharField("contato de emergência - telefone", max_length=30, blank=True)
    emergency_contact_relationship = models.CharField("contato de emergência - relação", max_length=60, blank=True)

    share_medical_info = models.BooleanField("compartilhar ficha médica no perfil público", default=False)

    is_active = models.BooleanField("ativo", default=True)

    created_at = models.DateTimeField("criado em", auto_now_add=True)
    updated_at = models.DateTimeField("atualizado em", auto_now=True)

    # Relaçoes externas
    guardians = models.ManyToManyField(
        "accounts.GuardianProfile",
        through="links.GuardianElderLink",
        related_name="elders",
        blank=True,
    )

    institutions = models.ManyToManyField(
        "accounts.InstitutionProfile",
        through="links.InstitutionElderLink",
        related_name="elders",
        blank=True,
    )

    caregivers = models.ManyToManyField(
        "accounts.CaregiverProfile",
        through="links.CaregiverElderLink",
        related_name="elders",
        blank=True,
    )
    
    professionals = models.ManyToManyField(
        "accounts.ProfessionalProfile",
        through="links.ProfessionalElderLink",
        related_name="elders",
        blank=True,
    )


    def __str__(self) -> str:
        return f"Idoso: {self.user.email}"
