from django.db import models


class VisibilityScope(models.TextChoices):
    PUBLIC = "PUBLIC", "Público"
    CAREGIVERS = "CAREGIVERS", "Cuidadores"
    ELDERS = "ELDERS", "Idosos"
    INSTITUTIONS = "INSTITUTIONS", "Instituições"
    PROFESSIONALS = "PROFESSIONALS", "Profissionais"
    GUARDIANS = "GUARDIANS", "Responsáveis"
    PRIVATE = "PRIVATE", "Privado"
