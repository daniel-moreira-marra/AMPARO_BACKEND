from django.db import IntegrityError, transaction
from django.db.models import Case, F, IntegerField, Value, When

from accounts.models import User
from core.cache import bump_feed_version
from core.exceptions import domain as domain_exceptions
from posts.models import Post, PostLike


@transaction.atomic
def like_post(*, actor: User, post_id: int) -> PostLike:
    try:
        post = Post.objects.select_for_update().get(id=post_id)
    except Post.DoesNotExist:
        raise domain_exceptions.NotFoundError(
            f"Post {post_id} not found.",
            code="post_not_found",
        )

    try:
        post_like = PostLike.objects.create(user=actor, post=post)
    except IntegrityError as exc:
        raise domain_exceptions.ConflictError(
            "User already liked this post.",
            code="post_already_liked",
        ) from exc

    Post.objects.filter(id=post.id).update(likes_count=F("likes_count") + 1)
    post.refresh_from_db(fields=["likes_count"])
    bump_feed_version()

    # Reuse the loaded post with the updated counter in the response layer.
    post_like.post = post
    return post_like


@transaction.atomic
def unlike_post(*, actor: User, post_id: int) -> None:
    try:
        post = Post.objects.select_for_update().get(id=post_id)
    except Post.DoesNotExist:
        raise domain_exceptions.NotFoundError(
            f"Post {post_id} not found.",
            code="post_not_found",
        )

    deleted_count, _ = PostLike.objects.filter(user_id=actor.id, post_id=post.id).delete()
    if deleted_count == 0:
        raise domain_exceptions.NotFoundError(
            "Like for this user and post not found.",
            code="post_like_not_found",
        )

    Post.objects.filter(id=post.id).update(
        likes_count=Case(
            When(likes_count__gt=0, then=F("likes_count") - 1),
            default=Value(0),
            output_field=IntegerField(),
        )
    )
    bump_feed_version()
