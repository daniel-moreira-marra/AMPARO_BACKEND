from django.db.models import QuerySet
from ..models import Post
from ..enums.post_status import PostStatus
from ..enums.visibility_scope import VisibilityScope
from accounts.enums import UserRole


def get_feed_queryset(*, user) -> QuerySet[Post]:
    """
    Retorna o queryset do feed geral.
    Centralizar aqui evita duplicar regras de visibilidade em vários lugares.
    """
    qs = Post.objects.filter(status=PostStatus.PUBLISHED)

    # Soft delete (se existir)
    if hasattr(Post, "deleted_at"):
        qs = qs.filter(deleted_at__isnull=True)

    # Visibilidade: exemplo simples (ajuste conforme seu domínio)
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
        
    # Se não estiver autenticado, só PUBLIC
    if user is None or not getattr(user, "is_authenticated", False):
        allowed_scopes = [VisibilityScope.PUBLIC]

    qs = qs.filter(visibility_scope__in=allowed_scopes)

    # A ordenação é aplicada pelo CursorPagination na view, não aqui
    # Isso evita conflitos entre a ordenação do queryset e do paginador
    return qs
