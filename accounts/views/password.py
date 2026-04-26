from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, serializers
from drf_spectacular.utils import extend_schema, OpenApiExample

from ..serializers import ChangePasswordSerializer
from ..services.user_services import change_user_password
from core.exceptions.responses import success_response
from core.docs.schemas import ERROR_400_BAD_REQUEST, ERROR_401_UNAUTHORIZED


class ChangePasswordSuccessSerializer(serializers.Serializer):
    message = serializers.CharField(help_text="Mensagem de confirmação.")


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Auth"],
        summary="Alterar senha",
        description=(
            "Altera a senha do usuário autenticado.\n\n"
            "**Validações:**\n"
            "- `old_password` deve corresponder à senha atual\n"
            "- `new_password` deve ter no mínimo 8 caracteres"
        ),
        request=ChangePasswordSerializer,
        responses={
            200: ChangePasswordSuccessSerializer,
            400: ERROR_400_BAD_REQUEST,
            401: ERROR_401_UNAUTHORIZED,
        },
        examples=[
            OpenApiExample(
                "Requisição",
                value={
                    "old_password": "senhaAntiga123",
                    "new_password": "senhaNova456",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Senha alterada com sucesso",
                value={
                    "success": True,
                    "data": None,
                    "message": "Password changed successfully.",
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Senha atual incorreta",
                value={
                    "success": False,
                    "error": {
                        "code": "validation_error",
                        "message": "Senha atual incorreta.",
                        "details": None,
                    },
                },
                response_only=True,
                status_codes=["400"],
            ),
        ],
    )
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        change_user_password(user=request.user, data=serializer.validated_data)
        return success_response(data=None, message="Password changed successfully.")
