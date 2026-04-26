from django.db import models
from django.conf import settings

from ..enums import PostStatus
from ..enums import VisibilityScope

class Post(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )

    author_role = models.CharField(max_length=20)

    text = models.TextField()
    image = models.ImageField(upload_to="post-images/", null=True, blank=True)
    image_alt_text = models.CharField(max_length=255, blank=True)

    status = models.CharField(
        max_length=20,
        choices=PostStatus.choices,
        default=PostStatus.PUBLISHED,
    )

    visibility_scope = models.CharField(
        max_length=20,
        choices=VisibilityScope.choices,
        default=VisibilityScope.PUBLIC,
    )

    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)

    parent_post = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reposts",
    )

    tags = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)


