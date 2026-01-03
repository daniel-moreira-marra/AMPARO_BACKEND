from django.db import models


class CareType(models.TextChoices):
    HOME = "HOME", "Domiciliar"
    HOSPITAL = "HOSPITAL", "Hospitalar"
    NIGHT_SHIFT = "NIGHT_SHIFT", "Plantão noturno"
    DAY_SHIFT = "DAY_SHIFT", "Plantão diurno"
    COMPANION = "COMPANION", "Acompanhante"

class ServiceMode(models.TextChoices):
    HOME = "HOME", "Domiciliar"
    CLINIC = "CLINIC", "Em clínica"
    ONLINE = "ONLINE", "Online"
    OTHER = "OTHER", "Outro"