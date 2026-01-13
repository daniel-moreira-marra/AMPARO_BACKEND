from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.exceptions.handlers import deny_role

from ..models import InstitutionProfile
from ..serializers import InstitutionMeSerializer
from ..docs import (
    institution_me_get_docs,
    institution_me_patch_docs,
    institution_me_put_docs,
)


class InstitutionMeView(APIView):
    """
    Permite que o próprio usuário com role=INSTITUTION consulte/atualize seu InstitutionProfile.
    """
    permission_classes = [IsAuthenticated]

    def _ensure_role(self, user):
        if getattr(user, "role", None) != "INSTITUTION":
            deny_role("INSTITUTION")
        return None

    def _get_profile(self, user):
        profile, _ = InstitutionProfile.objects.get_or_create(user=user)
        return profile

    @institution_me_get_docs()
    def get(self, request):
        forbidden = self._ensure_role(request.user)
        if forbidden:
            return forbidden

        profile = self._get_profile(request.user)
        return Response(InstitutionMeSerializer(profile).data, status=status.HTTP_200_OK)

    @institution_me_patch_docs()
    def patch(self, request):
        forbidden = self._ensure_role(request.user)
        if forbidden:
            return forbidden

        profile = self._get_profile(request.user)
        serializer = InstitutionMeSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @institution_me_put_docs()
    def put(self, request):
        forbidden = self._ensure_role(request.user)
        if forbidden:
            return forbidden

        profile = self._get_profile(request.user)
        serializer = InstitutionMeSerializer(profile, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
