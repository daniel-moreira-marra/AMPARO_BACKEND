from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import extend_schema, OpenApiExample

from ..docs import me_docs

from ..serializers import MeSerializer, UpdateMeSerializer
from ..services.user_services import update_user_profile
from core.exceptions.responses import success_response
from core.docs.schemas import (
    get_success_response_serializer,
    ERROR_400_BAD_REQUEST,
    ERROR_401_UNAUTHORIZED,
)


class MeView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @me_docs()
    def get(self, request):
        return success_response(data=MeSerializer(request.user).data)

    @extend_schema(
        tags=["Auth"],
        summary="Atualizar perfil do usuário logado",
        description=(
            "Atualiza parcialmente os dados do usuário autenticado. "
            "Todos os campos são opcionais (PATCH semântico).\n\n"
            "**Upload de avatar:** envie o campo `avatar` como `multipart/form-data`.\n\n"
            "**Campos de privacidade:** `show_email`, `show_phone` e `show_links` "
            "controlam o que é exibido no perfil público."
        ),
        request=UpdateMeSerializer,
        responses={
            200: get_success_response_serializer(MeSerializer),
            400: ERROR_400_BAD_REQUEST,
            401: ERROR_401_UNAUTHORIZED,
        },
        examples=[
            OpenApiExample(
                "Atualizar nome e endereço",
                value={
                    "full_name": "Maria Aparecida Silva",
                    "phone": "(11) 98765-4321",
                    "city": "São Paulo",
                    "state": "SP",
                    "zip_code": "01310-100",
                    "address_line": "Av. Paulista, 1000, Apto 42",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Configurar privacidade",
                value={
                    "show_email": False,
                    "show_phone": True,
                    "show_links": True,
                },
                request_only=True,
            ),
            OpenApiExample(
                "Resposta de sucesso",
                value={
                    "success": True,
                    "data": {
                        "id": 1,
                        "email": "maria@email.com",
                        "full_name": "Maria Aparecida Silva",
                        "phone": "(11) 98765-4321",
                        "avatar": "https://storage.exemplo.com/avatars/1.jpg",
                        "role": "CAREGIVER",
                        "is_verified": True,
                        "onboarding_completed": True,
                        "show_email": False,
                        "show_phone": True,
                        "show_links": True,
                        "address_line": "Av. Paulista, 1000, Apto 42",
                        "city": "São Paulo",
                        "state": "SP",
                        "zip_code": "01310-100",
                    },
                },
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def patch(self, request):
        serializer = UpdateMeSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        user = update_user_profile(user=request.user, data=serializer.validated_data)
        return success_response(data=MeSerializer(user).data)
