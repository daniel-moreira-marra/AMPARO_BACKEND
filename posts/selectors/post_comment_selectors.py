from django.db.models import QuerySet

from core.exceptions import domain as domain_exceptions
from posts.models import Post, PostComment


def get_post_comments_queryset(*, post_id: int) -> QuerySet[PostComment]:
    try:
        Post.objects.only("id").get(id=post_id)
    except Post.DoesNotExist:
        raise domain_exceptions.NotFoundError(
            f"Post {post_id} not found.",
            code="post_not_found",
        )

    return PostComment.objects.filter(post_id=post_id).select_related("user").order_by("-created_at")
