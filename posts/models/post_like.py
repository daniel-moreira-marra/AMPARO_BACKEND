from django.conf import settings
from django.db import models

from .posts import Post

class PostLike(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="post_likes",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"],
                name="posts_postlike_unique_user_post",
            ),
        ]
        indexes = [
            models.Index(fields=["post", "created_at"], name="posts_plike_post_created_idx"),
            models.Index(fields=["user", "created_at"], name="posts_plike_user_created_idx"),
        ]
