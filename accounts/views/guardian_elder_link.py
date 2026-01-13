from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from drf_spectacular.utils import extend_schema, extend_schema_view

from ..models import GuardianElderLink, GuardianProfile
from ..serializers.guardian_elder_link import GuardianElderLinkSerializer
from ..permissions import IsGuardianRole
from ..docs import guardian_elder_link_docs

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

    def perform_create(self, serializer):
        # guardian é sempre do usuário logado
        serializer.save()
