from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.exceptions.handlers import deny_role

from ..models import ProfessionalProfile
from ..serializers.professional_me import ProfessionalMeSerializer
from ..docs import (
    professional_me_get_docs,
    professional_me_patch_docs,
    professional_me_put_docs,
)


class ProfessionalMeView(APIView):
    permission_classes = [IsAuthenticated]

    def _ensure_role(self, user):
        if getattr(user, "role", None) != "PROFESSIONAL":
            deny_role("PROFESSIONAL")
        return None

    def _get_profile(self, user):
        profile, _ = ProfessionalProfile.objects.get_or_create(user=user)
        return profile

    @professional_me_get_docs()
    def get(self, request):
        forbidden = self._ensure_role(request.user)
        if forbidden:
            return forbidden

        profile = self._get_profile(request.user)
        return Response(
            ProfessionalMeSerializer(profile).data,
            status=status.HTTP_200_OK,
        )

    @professional_me_patch_docs()
    def patch(self, request):
        forbidden = self._ensure_role(request.user)
        if forbidden:
            return forbidden

        profile = self._get_profile(request.user)
        serializer = ProfessionalMeSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @professional_me_put_docs()
    def put(self, request):
        forbidden = self._ensure_role(request.user)
        if forbidden:
            return forbidden

        profile = self._get_profile(request.user)
        serializer = ProfessionalMeSerializer(profile, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
