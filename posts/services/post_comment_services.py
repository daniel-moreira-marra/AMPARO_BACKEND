from django.db import transaction
from django.db.models import Case, F, IntegerField, Value, When

from accounts.models import User
from core.cache import bump_feed_version
from core.exceptions import domain as domain_exceptions
from posts.models import Post, PostComment


@transaction.atomic
def create_post_comment(*, actor: User, post_id: int, content: str) -> PostComment:
    try:
        post = Post.objects.select_for_update().get(id=post_id)
    except Post.DoesNotExist:
        raise domain_exceptions.NotFoundError(
            f"Post {post_id} not found.",
            code="post_not_found",
        )

    post_comment = PostComment.objects.create(
        user=actor,
        post=post,
        content=content,
    )

    Post.objects.filter(id=post.id).update(comments_count=F("comments_count") + 1)
    post.refresh_from_db(fields=["comments_count"])
    bump_feed_version()

    # Reuse the loaded post with the updated counter in the response layer.
    post_comment.post = post
    return post_comment


@transaction.atomic
def update_post_comment(*, actor: User, post_id: int, comment_id: int, content: str) -> PostComment:
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        raise domain_exceptions.NotFoundError(
            f"Post {post_id} not found.",
            code="post_not_found",
        )

    try:
        post_comment = PostComment.objects.select_related("post").get(
            id=comment_id,
            post_id=post.id,
        )
    except PostComment.DoesNotExist:
        raise domain_exceptions.NotFoundError(
            f"Comment {comment_id} for post {post_id} not found.",
            code="post_comment_not_found",
        )

    can_edit = actor.is_staff or post_comment.user_id == actor.id
    if not can_edit:
        raise domain_exceptions.PermissionDenied(
            "You do not have permission to edit this comment.",
            code="comment_permission_denied",
        )

    post_comment.content = content
    post_comment.save()
    bump_feed_version()
    return post_comment


@transaction.atomic
def delete_post_comment(*, actor: User, post_id: int, comment_id: int) -> None:
    try:
        post = Post.objects.select_for_update().get(id=post_id)
    except Post.DoesNotExist:
        raise domain_exceptions.NotFoundError(
            f"Post {post_id} not found.",
            code="post_not_found",
        )

    try:
        post_comment = PostComment.objects.select_for_update().get(
            id=comment_id,
            post_id=post.id,
        )
    except PostComment.DoesNotExist:
        raise domain_exceptions.NotFoundError(
            f"Comment {comment_id} for post {post_id} not found.",
            code="post_comment_not_found",
        )

    can_delete = (
        actor.is_staff
        or post_comment.user_id == actor.id
        or post.author_id == actor.id
    )
    if not can_delete:
        raise domain_exceptions.PermissionDenied(
            "You do not have permission to delete this comment.",
            code="comment_permission_denied",
        )

    deleted_count, _ = PostComment.objects.filter(id=post_comment.id, post_id=post.id).delete()
    if deleted_count == 0:
        raise domain_exceptions.NotFoundError(
            f"Comment {comment_id} for post {post_id} not found.",
            code="post_comment_not_found",
        )

    Post.objects.filter(id=post.id).update(
        comments_count=Case(
            When(comments_count__gt=0, then=F("comments_count") - 1),
            default=Value(0),
            output_field=IntegerField(),
        )
    )
    bump_feed_version()
