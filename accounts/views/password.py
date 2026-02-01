from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from ..serializers import ChangePasswordSerializer
from ..services.user_services import change_user_password
from core.exceptions.responses import success_response

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        change_user_password(user=request.user, data=serializer.validated_data)
        return success_response(data=None, message="Password changed successfully.")
