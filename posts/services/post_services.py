from django.db import transaction
from django.utils import timezone
from typing import Optional, Dict, Any

from core.exceptions import domain as domain_exceptions
from core.events import dispatch
from posts.models.posts import Post
from posts.enums.visibility_scope import VisibilityScope
from accounts.models import User
from core.cache import bump_feed_version

@transaction.atomic
def create_post(
    *,
    actor: User,
    data: Dict[str, Any],
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> Post:
    """
    Service to create a new post.
    
    Args:
        actor: The user creating the post.
        data: Validated data (text, visibility_scope, parent_post_id, etc.)
        ip_address: Optional IP address of the creator.
        user_agent: Optional User Agent of the creator.
    """
    text = data.get("text")
    if not text or not text.strip():
        raise domain_exceptions.ValidationError("Post text is required.", code="missing_text")

    visibility_scope = data.get("visibility_scope", VisibilityScope.PUBLIC)
    parent_post_id = data.get("parent_post_id")
    image = data.get("image")
    image_alt_text = data.get("image_alt_text", "")

    parent_post = None
    if parent_post_id:
        try:
            parent_post = Post.objects.get(id=parent_post_id)
        except Post.DoesNotExist:
            raise domain_exceptions.NotFoundError(f"Parent post {parent_post_id} not found.")

    # Business rule: Check if author can reply to this post (e.g. if it's not deleted)
    if parent_post and parent_post.deleted_at:
        raise domain_exceptions.ValidationError("Cannot reply to a deleted post.", code="inactive_parent")

    post = Post.objects.create(
        author=actor,
        text=text,
        image=image,
        image_alt_text=image_alt_text,
        visibility_scope=visibility_scope,
        parent_post=parent_post,
        published_at=timezone.now(),
        # Other fields like author_role could be derived here
        author_role=getattr(actor, "role", "user") 
    )

    # Dispatch event
    dispatch("post_created", post_id=post.id, actor_id=actor.id)
    
    # Invalidate feed cache
    bump_feed_version()

    return post


@transaction.atomic
def delete_post(*, actor: User, post_id: int) -> None:
    """
    Service to soft-delete a post.
    """
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        raise domain_exceptions.NotFoundError(f"Post {post_id} not found.")

    # Business rule: Only author or staff can delete
    if post.author != actor and not actor.is_staff:
        raise domain_exceptions.PermissionDenied("You do not have permission to delete this post.")

    if post.deleted_at:
        raise domain_exceptions.ValidationError("Post is already deleted.")

    post.deleted_at = timezone.now()
    post.save()

    # Dispatch event
    dispatch("post_deleted", post_id=post.id, actor_id=actor.id)

    # Invalidate feed cache
    bump_feed_version()
