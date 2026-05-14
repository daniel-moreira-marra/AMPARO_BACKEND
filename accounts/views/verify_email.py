from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from accounts.services.user_services import verify_user_email
from core.exceptions.domain import ValidationError

class VerifyEmailView(APIView):
    permission_classes = [AllowAny] # Rota pública, pois o usuário ainda não logou
    
    def post(self, request, *args, **kwargs):
        uid = request.data.get("uid")
        token = request.data.get("token")
        
        if not uid or not token:
            return Response({"detail": "UID e Token são obrigatórios."}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            verify_user_email(uid=uid, token=token)
            return Response({"detail": "E-mail verificado com sucesso."}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)