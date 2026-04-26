from django.db import models


class PostImage(models.Model):
    post = models.ForeignKey(
        "posts.Post",
        on_delete=models.CASCADE,
        related_name="post_images",
    )
    image = models.ImageField(upload_to="post-images/")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]
