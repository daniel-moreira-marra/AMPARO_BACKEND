from django.db import models
from django.conf import settings


class Notification(models.Model):
    LINK_REQUEST = "LINK_REQUEST"
    LINK_ACCEPTED = "LINK_ACCEPTED"

    TYPE_CHOICES = [
        (LINK_REQUEST, "Solicitação de vínculo"),
        (LINK_ACCEPTED, "Vínculo aceito"),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    type = models.CharField(max_length=30, choices=TYPE_CHOICES)
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    actor_name = models.CharField(max_length=150, blank=True)
    link_type = models.CharField(max_length=30, blank=True)
    link_id = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read", "-created_at"]),
        ]
