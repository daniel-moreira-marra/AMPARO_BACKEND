from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from ..models import InstitutionElderLink
from ..serializers import InstitutionElderLinkSerializer
from ..docs import (
    institution_elder_links_list_docs,
    institution_elder_links_create_docs,
    institution_elder_links_retrieve_docs,
    institution_elder_links_patch_docs,
    institution_elder_links_put_docs,
    institution_elder_links_delete_docs,
)

from core.exceptions.helpers import deny_role
from core.exceptions.responses import success_response, wrap_success_response


class InstitutionElderLinkViewSet(viewsets.ModelViewSet):
    """
    CRUD dos vínculos Institution ↔ Elder.

    Escopo:
    - A instituição só acessa/edita vínculos do seu próprio InstitutionProfile.
    """
    serializer_class = InstitutionElderLinkSerializer
    permission_classes = [IsAuthenticated]

    def _ensure_role(self, user):
        print(user.role)
        if getattr(user, "role", None) != "INSTITUTION":
            deny_role("INSTITUTION")
        return None

    def _institution_profile(self):
        user = self.request.user
        self._ensure_role(user)

        profile = getattr(user, "institution_profile", None)
        if profile is None:
            raise PermissionDenied("Usuário não possui InstitutionProfile.")
        return profile

    def get_queryset(self):
        return (
            InstitutionElderLink.objects.filter(institution=self._institution_profile())
            .select_related("elder", "institution")
            .order_by("-is_active", "-created_at")
        )

    @institution_elder_links_list_docs()
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return wrap_success_response(response=response)

    @institution_elder_links_create_docs()
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return wrap_success_response(response=response)

    @institution_elder_links_retrieve_docs()
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return wrap_success_response(response=response)

    @institution_elder_links_patch_docs()
    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        return wrap_success_response(response=response)

    @institution_elder_links_put_docs()
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return wrap_success_response(response=response)

    @institution_elder_links_delete_docs()
    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        return success_response(
            data=None,
            status_code=status.HTTP_200_OK,
            headers=response.headers,
        )
