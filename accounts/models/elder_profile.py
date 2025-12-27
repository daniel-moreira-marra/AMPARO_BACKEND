from django.conf import settings
from django.db import models


class ElderProfile(models.Model):
    """
    Dados específicos do idoso.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="elder_profile",
    )

    birth_date = models.DateField(null=True, blank=True)
    medical_notes = models.TextField(blank=True)

    def __str__(self):
        return f"Idoso: {self.user.email}"
