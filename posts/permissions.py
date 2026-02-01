from rest_framework import permissions
from .enums import VisibilityScope
from accounts.models.caregiver_elder_link import CaregiverElderLink
from accounts.enums import UserRole

class IsPostOwner(permissions.BasePermission):
    """
    Permissão que garante que apenas o autor do post pode editá-lo ou deletá-lo.
    """
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user

class CanViewPost(permissions.BasePermission):
    """
    Permissão que decide se o usuário pode visualizar o post baseado em:
    - Se é o dono (sempre pode)
    - Escopo de visibilidade (PUBLIC, PRIVATE, etc.)
    - Vínculo ativo (para visibilidade restrita)
    """
    def has_object_permission(self, request, view, obj):
        # 1. Dono sempre pode ver
        if obj.author == request.user:
            return True

        # 2. Público sempre visível
        if obj.visibility_scope == VisibilityScope.PUBLIC:
            return True

        # Se for privado e não for o dono, bloqueia logo
        if obj.visibility_scope == VisibilityScope.PRIVATE:
            return False

        # 3. Verificação de autenticação para os demais escopos
        if not request.user or not request.user.is_authenticated:
            return False

        # 4. Verificação de papel (Role) e Vínculo (Link)
        # Se o post é para CAREGIVERS, o usuário deve ser cuidador e ter vínculo ativo com o idoso (autor)
        if obj.visibility_scope == VisibilityScope.CAREGIVERS:
            if request.user.role != UserRole.CAREGIVER:
                return False
            
            # Verifica se existe vínculo ativo entre o cuidador atual e o idoso autor
            # Supomos que o autor seja um ELDER se a visibilidade é para cuidadores
            return CaregiverElderLink.objects.filter(
                caregiver__user=request.user,
                elder__user=obj.author,
                status=CaregiverElderLink.Status.ACTIVE
            ).exists()

        # Se o post é para ELDERS, o usuário deve ser idoso e ter vínculo com o autor (que pode ser cuidador ou outro idoso)
        if obj.visibility_scope == VisibilityScope.ELDERS:
            if request.user.role != UserRole.ELDER:
                return False
            
            # Aqui a lógica pode variar: se o autor é um caregiver, checa vínculo normal.
            # Se fosse um post de um idoso para outros idosos, a lógica seria diferente, 
            # mas o requisito foca no vínculo caregiver-elder.
            return CaregiverElderLink.objects.filter(
                elder__user=request.user,
                caregiver__user=obj.author,
                status=CaregiverElderLink.Status.ACTIVE
            ).exists()

        # Para outros escopos (GUARDIANS, etc.), poderíamos implementar lógica similar.
        # Por padrão, se não cair em nenhum acima e não for dono/público, negamos.
        return False

class CanEditPost(IsPostOwner):
    """
    Explicitamente usado para edição. Atualmente igual ao IsPostOwner,
    mas separado para facilitar regras de negócio futuras (ex: admin pode editar).
    """
    pass
