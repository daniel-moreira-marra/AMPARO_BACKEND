from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied

from core.exceptions.handlers import deny_role

from ..models import ElderProfile
from ..serializers.elder_me import ElderMeSerializer

from ..docs import (
    elder_me_get_docs,
    elder_me_patch_docs,
    elder_me_put_docs,
)


class ElderMeView(APIView):
    """
    Permite que o próprio usuário com role=ELDER consulte/atualize seu ElderProfile.
    """
    permission_classes = [IsAuthenticated]

    def _get_elder_profile(self, user):
        """
        Retorna o ElderProfile do usuário.
        Se não existir por algum motivo, cria (evita 500 em ambientes inconsistentes).
        """
        profile, _ = ElderProfile.objects.get_or_create(user=user)
        return profile

    def _ensure_elder_role(self, user) -> Response | None:
        """
        Garante que apenas usuários com role ELDER usem este endpoint.
        Retorna uma Response 403 se não for ELDER; caso contrário, None.
        """
        if getattr(user, "role", None) != "ELDER":
            deny_role("ELDER")
        return None

    @elder_me_get_docs()
    def get(self, request):
        forbidden = self._ensure_elder_role(request.user)
        if forbidden:
            return forbidden

        profile = self._get_elder_profile(request.user)
        return Response(ElderMeSerializer(profile).data, status=status.HTTP_200_OK)

    @elder_me_patch_docs()
    def patch(self, request):
        forbidden = self._ensure_elder_role(request.user)
        if forbidden:
            return forbidden

        profile = self._get_elder_profile(request.user)
        serializer = ElderMeSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @elder_me_put_docs()
    def put(self, request):
        forbidden = self._ensure_elder_role(request.user)
        if forbidden:
            return forbidden

        profile = self._get_elder_profile(request.user)
        serializer = ElderMeSerializer(profile, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
