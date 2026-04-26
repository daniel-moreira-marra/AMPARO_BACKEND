from django.db.models import Q, QuerySet, Exists, OuterRef
from ..models import Post, PostLike
from ..enums.post_status import PostStatus
from ..enums.visibility_scope import VisibilityScope
from accounts.enums import UserRole


def get_feed_queryset(*, user, q: str = "", role_filter: str = "", tag: str = "") -> QuerySet[Post]:
    """
    Retorna o queryset do feed geral com suporte a filtros opcionais.
    """
    qs = Post.objects.filter(status=PostStatus.PUBLISHED)

    if hasattr(Post, "deleted_at"):
        qs = qs.filter(deleted_at__isnull=True)

    allowed_scopes = [VisibilityScope.PUBLIC]

    user_role = getattr(user, "role", None)
    if user_role == UserRole.CAREGIVER:
        allowed_scopes.append(VisibilityScope.CAREGIVERS)
    elif user_role == UserRole.ELDER:
        allowed_scopes.append(VisibilityScope.ELDERS)
    elif user_role == UserRole.GUARDIAN:
        allowed_scopes.append(VisibilityScope.GUARDIANS)
    elif user_role == UserRole.INSTITUTION:
        allowed_scopes.append(VisibilityScope.INSTITUTIONS)
    elif user_role == UserRole.PROFESSIONAL:
        allowed_scopes.append(VisibilityScope.PROFESSIONALS)

    if user is None or not getattr(user, "is_authenticated", False):
        allowed_scopes = [VisibilityScope.PUBLIC]

    qs = qs.filter(visibility_scope__in=allowed_scopes)

    if q:
        qs = qs.filter(Q(text__icontains=q) | Q(author__full_name__icontains=q))

    if role_filter:
        qs = qs.filter(author_role=role_filter.upper())

    if tag:
        qs = qs.filter(tags__icontains=tag.lower())

    qs = qs.select_related("author", "parent_post", "parent_post__author")
    qs = qs.prefetch_related("post_images", "parent_post__post_images")

    if user and getattr(user, "is_authenticated", False):
        qs = qs.annotate(
            _liked_by_me=Exists(
                PostLike.objects.filter(post=OuterRef("pk"), user=user)
            )
        )

    return qs
