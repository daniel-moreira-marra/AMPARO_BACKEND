from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from core.exceptions.responses import success_response

User = get_user_model()


class PublicUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = get_object_or_404(User, id=pk, is_active=True)
        avatar_url = None
        if user.avatar:
            try:
                avatar_url = request.build_absolute_uri(user.avatar.url)
            except Exception:
                pass
        return success_response(data={
            "id": user.id,
            "full_name": user.full_name,
            "role": user.role,
            "avatar": avatar_url,
            "city": user.city or None,
            "state": user.state or None,
        })
