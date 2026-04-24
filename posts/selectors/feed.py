from django.db.models import QuerySet, Exists, OuterRef
from ..models import Post, PostLike
from ..enums.post_status import PostStatus
from ..enums.visibility_scope import VisibilityScope
from accounts.enums import UserRole


def get_feed_queryset(*, user) -> QuerySet[Post]:
    """
    Retorna o queryset do feed geral.
    Centralizar aqui evita duplicar regras de visibilidade em vários lugares.
    """
    qs = Post.objects.filter(status=PostStatus.PUBLISHED)

    if hasattr(Post, "deleted_at"):
        qs = qs.filter(deleted_at__isnull=True)

    allowed_scopes = [VisibilityScope.PUBLIC]

    role = getattr(user, "role", None)
    if role == UserRole.CAREGIVER:
        allowed_scopes.append(VisibilityScope.CAREGIVERS)
    elif role == UserRole.ELDER:
        allowed_scopes.append(VisibilityScope.ELDERS)
    elif role == UserRole.GUARDIAN:
        allowed_scopes.append(VisibilityScope.GUARDIANS)
    elif role == UserRole.INSTITUTION:
        allowed_scopes.append(VisibilityScope.INSTITUTIONS)
    elif role == UserRole.PROFESSIONAL:
        allowed_scopes.append(VisibilityScope.PROFESSIONALS)

    if user is None or not getattr(user, "is_authenticated", False):
        allowed_scopes = [VisibilityScope.PUBLIC]

    qs = qs.filter(visibility_scope__in=allowed_scopes)

    # Evitar N+1 ao serializar author, parent_post e author do parent_post
    qs = qs.select_related("author", "parent_post", "parent_post__author")

    # Anotar liked_by_me para usuários autenticados (evita N+1 por post)
    if user and getattr(user, "is_authenticated", False):
        qs = qs.annotate(
            _liked_by_me=Exists(
                PostLike.objects.filter(post=OuterRef("pk"), user=user)
            )
        )

    return qs
