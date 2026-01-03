from django.conf import settings
from django.db import models


class GuardianProfile(models.Model):
    """
    Perfil do RESPONSÁVEL (GUARDIAN).

    Ideia principal:
    - Guarda dados específicos do responsável.
    - Conecta um responsável a um ou mais idosos.
    """

    class Relationship(models.TextChoices):
        CHILD = "CHILD", "Filho(a)"
        SPOUSE = "SPOUSE", "Cônjuge"
        SIBLING = "SIBLING", "Irmão(ã)"
        RELATIVE = "RELATIVE", "Parente"
        LEGAL_GUARDIAN = "LEGAL_GUARDIAN", "Responsável legal"
        OTHER = "OTHER", "Outro"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="guardian_profile",
    )

    relationship = models.CharField(
        "relação com o idoso (principal)",
        max_length=30,
        choices=Relationship.choices,
        default=Relationship.OTHER,
    )

    is_legal_guardian = models.BooleanField("responsável legal", default=False)
    preferred_contact = models.CharField("forma de contato preferida", max_length=30, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"GuardianProfile<{self.user.email}>"
