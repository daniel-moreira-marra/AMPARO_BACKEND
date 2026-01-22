from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from core.exceptions.helpers import deny_role
from core.exceptions.responses import success_response, wrap_success_response

from ..models import ProfessionalElderLink
from ..serializers  import ProfessionalElderLinkSerializer
from ..docs import (
    professional_elder_links_list_docs,
    professional_elder_links_create_docs,
    professional_elder_links_retrieve_docs,
    professional_elder_links_patch_docs,
    professional_elder_links_put_docs,
    professional_elder_links_delete_docs,
)


class ProfessionalElderLinkViewSet(viewsets.ModelViewSet):
    """
    CRUD dos vínculos Professional ↔ Elder.

    Escopo:
    - O profissional só acessa/edita vínculos do seu próprio ProfessionalProfile.
    """
    serializer_class = ProfessionalElderLinkSerializer
    permission_classes = [IsAuthenticated]

    def _professional_profile(self):
        user = self.request.user
        if getattr(user, "role", None) != "PROFESSIONAL":
            deny_role("PROFESSIONAL")

        profile = getattr(user, "professional_profile", None)
        if profile is None:
            raise PermissionDenied("Usuário não possui ProfessionalProfile.")
        return profile

    def get_queryset(self):
        return (
            ProfessionalElderLink.objects.filter(professional=self._professional_profile())
            .select_related("elder", "professional")
            .order_by("-is_active", "-created_at")
        )

    @professional_elder_links_list_docs()
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return wrap_success_response(response=response)

    @professional_elder_links_create_docs()
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return wrap_success_response(response=response)

    @professional_elder_links_retrieve_docs()
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return wrap_success_response(response=response)

    @professional_elder_links_patch_docs()
    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        return wrap_success_response(response=response)

    @professional_elder_links_put_docs()
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return wrap_success_response(response=response)

    @professional_elder_links_delete_docs()
    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return success_response(
            data=None,
            status_code=status.HTTP_200_OK,
            headers=response.headers,
        )
