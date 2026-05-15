from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from accounts.services.user_services import verify_user_email, request_password_reset, reset_password_with_token
from core.exceptions.domain import ValidationError

# 1. Rota de Verificar E-mail
class VerifyEmailView(APIView):
    permission_classes = [AllowAny]
    
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

# 2. Rota de Pedir Nova Senha (Esqueci a senha)
class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        if not email:
            return Response({"detail": "E-mail é obrigatório."}, status=status.HTTP_400_BAD_REQUEST)
            
        request_password_reset(email=email)
        # Por segurança, avisamos que enviamos mesmo que o e-mail não exista
        return Response({"detail": "Se o e-mail existir, as instruções foram enviadas."}, status=status.HTTP_200_OK)

# 3. Rota de Confirmar Nova Senha (Definir a senha nova)
class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        uid = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("new_password")
        
        if not all([uid, token, new_password]):
            return Response({"detail": "Dados incompletos."}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            reset_password_with_token(uid=uid, token=token, new_password=new_password)
            return Response({"detail": "Senha redefinida com sucesso."}, status=status.HTTP_200_OK)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)