from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.exceptions.helpers import deny_role
from core.exceptions.responses import success_response

from ..models import CaregiverProfile
from ..serializers import CaregiverMeSerializer
from ..docs import (
    caregiver_me_get_docs,
    caregiver_me_patch_docs,
    caregiver_me_put_docs,
)


class CaregiverMeView(APIView):
    """
    Permite que o próprio usuário com role=CAREGIVER consulte/atualize seu CaregiverProfile.
    """
    permission_classes = [IsAuthenticated]

    def _ensure_role(self, user) -> Response | None:
        if getattr(user, "role", None) != "CAREGIVER":
            deny_role("CAREGIVER")
        return None

    def _get_profile(self, user):
        profile, _ = CaregiverProfile.objects.get_or_create(user=user)
        return profile

    @caregiver_me_get_docs()
    def get(self, request):
        forbidden = self._ensure_role(request.user)
        if forbidden:
            return forbidden

        profile = self._get_profile(request.user)
        return success_response(
            data=CaregiverMeSerializer(profile).data,
            status_code=status.HTTP_200_OK,
        )

    @caregiver_me_patch_docs()
    def patch(self, request):
        forbidden = self._ensure_role(request.user)
        if forbidden:
            return forbidden

        profile = self._get_profile(request.user)
        serializer = CaregiverMeSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data, status_code=status.HTTP_200_OK)

    @caregiver_me_put_docs()
    def put(self, request):
        forbidden = self._ensure_role(request.user)
        if forbidden:
            return forbidden

        profile = self._get_profile(request.user)
        serializer = CaregiverMeSerializer(profile, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data, status_code=status.HTTP_200_OK)
