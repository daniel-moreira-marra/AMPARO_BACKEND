from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from drf_spectacular.utils import extend_schema, extend_schema_view

from ..models import GuardianElderLink, GuardianProfile
from ..serializers.guardian_elder_link import GuardianElderLinkSerializer
from ..permissions import IsGuardianRole
from ..docs import guardian_elder_link_docs
from core.exceptions.responses import success_response, wrap_success_response

@guardian_elder_link_docs()
class GuardianElderLinkViewSet(viewsets.ModelViewSet):
    """
    CRUD dos vínculos Guardian ↔ Elder.

    Escopo:
    - O guardian só acessa/edita vínculos do seu próprio GuardianProfile.
    """
    serializer_class = GuardianElderLinkSerializer
    permission_classes = [IsAuthenticated, IsGuardianRole]

    def _guardian_profile(self) -> GuardianProfile:
        profile = getattr(self.request.user, "guardian_profile", None)
        if profile is None:
            # role=GUARDIAN mas perfil não existe: estado inconsistente
            raise PermissionDenied("Usuário não possui GuardianProfile.")
        return profile

    def get_queryset(self):
        return GuardianElderLink.objects.filter(guardian=self._guardian_profile()).select_related("elder", "guardian")

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return wrap_success_response(response=response)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return wrap_success_response(response=response)

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return wrap_success_response(response=response)

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        return wrap_success_response(response=response)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return wrap_success_response(response=response)

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return success_response(
            data=None,
            status_code=status.HTTP_200_OK,
            headers=response.headers,
        )

    def perform_create(self, serializer):
        # guardian é sempre do usuário logado
        serializer.save()
