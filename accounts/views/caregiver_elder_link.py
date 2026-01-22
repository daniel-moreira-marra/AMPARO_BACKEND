from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from core.exceptions.helpers import deny_role
from core.exceptions.responses import success_response, wrap_success_response

from ..models import CaregiverElderLink
from ..serializers.caregiver_elder_link import CaregiverElderLinkSerializer
from ..docs import (
    caregiver_elder_links_list_docs,
    caregiver_elder_links_create_docs,
    caregiver_elder_links_retrieve_docs,
    caregiver_elder_links_patch_docs,
    caregiver_elder_links_put_docs,
    caregiver_elder_links_delete_docs,
)


class CaregiverElderLinkViewSet(viewsets.ModelViewSet):
    """
    CRUD dos vínculos Caregiver ↔ Elder.

    Escopo:
    - O cuidador só acessa/edita vínculos do seu próprio CaregiverProfile.
    """
    serializer_class = CaregiverElderLinkSerializer
    permission_classes = [IsAuthenticated]

    def _caregiver_profile(self):
        user = self.request.user
        if getattr(user, "role", None) != "CAREGIVER":
            deny_role("CAREGIVER")

        profile = getattr(user, "caregiver_profile", None)
        if profile is None:
            raise PermissionDenied("Usuário não possui CaregiverProfile.")
        return profile

    def get_queryset(self):
        return (
            CaregiverElderLink.objects.filter(caregiver=self._caregiver_profile())
            .select_related("elder", "caregiver")
            .order_by("-is_active", "-created_at")
        )

    @caregiver_elder_links_list_docs()
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return wrap_success_response(response=response)

    @caregiver_elder_links_create_docs()
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return wrap_success_response(response=response)

    @caregiver_elder_links_retrieve_docs()
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return wrap_success_response(response=response)

    @caregiver_elder_links_patch_docs()
    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        return wrap_success_response(response=response)

    @caregiver_elder_links_put_docs()
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return wrap_success_response(response=response)

    @caregiver_elder_links_delete_docs()
    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return success_response(
            data=None,
            status_code=status.HTTP_200_OK,
            headers=response.headers,
        )
