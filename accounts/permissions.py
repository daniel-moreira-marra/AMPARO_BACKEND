from rest_framework.permissions import BasePermission


class IsGuardianRole(BasePermission):
    """
    Permite acesso apenas para usuários com role=GUARDIAN.
    """
    message = "Apenas usuários do tipo GUARDIAN podem acessar este recurso."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, "role", None) == "GUARDIAN")
