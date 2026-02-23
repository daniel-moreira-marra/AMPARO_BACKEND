from django.conf import settings
from django.core.validators import MaxLengthValidator
from django.db import models

from .posts import Post


class PostComment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="post_comments",
    )
    content = models.TextField(validators=[MaxLengthValidator(500)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["post", "created_at"], name="posts_pc_post_created_idx"),
            models.Index(fields=["user", "created_at"], name="posts_pc_user_created_idx"),
        ]
