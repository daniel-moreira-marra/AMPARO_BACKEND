from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiExample

from core.exceptions.responses import success_response
from core.docs.schemas import (
    get_success_response_serializer,
    ERROR_401_UNAUTHORIZED,
)
from ..serializers import MeSerializer


class CompleteOnboardingView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Auth"],
        summary="Concluir onboarding",
        description=(
            "Marca o onboarding do usuário autenticado como concluído, "
            "liberando acesso às rotas protegidas da plataforma.\n\n"
            "**Quando chamar:** ao final do fluxo de onboarding, após o usuário "
            "preencher os dados do seu perfil de papel (Cuidador, Idoso, etc.).\n\n"
            "**Idempotente:** se o onboarding já estiver concluído, "
            "a chamada é ignorada e retorna os dados atuais normalmente."
        ),
        request=None,
        responses={
            200: get_success_response_serializer(MeSerializer),
            401: ERROR_401_UNAUTHORIZED,
        },
        examples=[
            OpenApiExample(
                "Onboarding concluído",
                value={
                    "success": True,
                    "data": {
                        "id": 5,
                        "email": "joao@email.com",
                        "full_name": "João da Silva",
                        "phone": "(11) 91234-5678",
                        "avatar": None,
                        "role": "CAREGIVER",
                        "is_verified": True,
                        "onboarding_completed": True,
                        "show_email": True,
                        "show_phone": True,
                        "show_links": True,
                        "address_line": "Rua das Flores, 10",
                        "city": "Campinas",
                        "state": "SP",
                        "zip_code": "13010-050",
                    },
                },
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def post(self, request):
        user = request.user
        if not user.onboarding_completed:
            user.onboarding_completed = True
            user.save(update_fields=["onboarding_completed"])
        return success_response(data=MeSerializer(user).data)
