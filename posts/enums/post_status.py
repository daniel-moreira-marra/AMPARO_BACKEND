from django.db import models


class PostStatus(models.TextChoices):
    DRAFT = "DRAFT", "Rascunho"
    PUBLISHED = "PUBLISHED", "Publicado"
    ARCHIVED = "ARCHIVED", "Arquivado"
    BLOCKED = "BLOCKED", "Bloqueado"
    DELETED = "DELETED", "Deletado"