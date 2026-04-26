from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from core.exceptions.responses import success_response
from core.docs.schemas import (
    get_success_response_serializer,
    ERROR_401_UNAUTHORIZED,
    ERROR_404_NOT_FOUND,
)

User = get_user_model()


class PublicProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="ID do usuário.")
    full_name = serializers.CharField(help_text="Nome completo.")
    role = serializers.ChoiceField(
        choices=["ELDER", "CAREGIVER", "GUARDIAN", "PROFESSIONAL", "INSTITUTION"],
        help_text="Papel do usuário na plataforma.",
    )
    avatar = serializers.URLField(allow_null=True, help_text="URL do avatar (null se não definido).")
    city = serializers.CharField(allow_null=True, help_text="Cidade.")
    state = serializers.CharField(allow_null=True, help_text="Estado (UF, ex: SP).")
    elder_profile_id = serializers.IntegerField(
        allow_null=True,
        help_text="ID do ElderProfile. Presente apenas se `role` for ELDER. Usado para acessar o prontuário.",
    )
    email = serializers.EmailField(
        allow_null=True,
        help_text="E-mail do usuário. Null se o usuário optou por não exibir (`show_email=false`).",
    )
    phone = serializers.CharField(
        allow_null=True,
        help_text="Telefone do usuário. Null se o usuário optou por não exibir (`show_phone=false`).",
    )
    show_links = serializers.BooleanField(help_text="Se os vínculos ativos devem ser exibidos no perfil.")
    profile = serializers.DictField(
        help_text=(
            "Dados do perfil específico do papel. Os campos variam conforme o `role`:\n\n"
            "- **ELDER**: `preferred_name`, `share_medical_info`, `medical_conditions`, `allergies`, `medications` (condicionais)\n"
            "- **CAREGIVER**: `bio`, `experience_years`, `is_available`, `care_types[]`, `city`, `state`\n"
            "- **PROFESSIONAL**: `profession`, `profession_other`, `council`, `license_number`, `bio`, `service_mode`, `hourly_rate`, `is_available`, `city`, `state`\n"
            "- **GUARDIAN**: `relationship`, `is_legal_guardian`\n"
            "- **INSTITUTION**: `legal_name`, `trade_name`, `institution_type`, `capacity`, `website`"
        )
    )


class PublicUserView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Usuários"],
        summary="Perfil público de um usuário",
        description=(
            "Retorna os dados públicos de qualquer usuário ativo pelo seu `id`.\n\n"
            "**Visibilidade condicional:**\n"
            "- `email` é retornado apenas se o usuário configurou `show_email=true`\n"
            "- `phone` é retornado apenas se o usuário configurou `show_phone=true`\n"
            "- `show_links` indica se o chamador deve exibir os vínculos do usuário\n\n"
            "**Perfil de papel (`profile`):** os campos dentro de `profile` variam conforme o `role`. "
            "Para idosos, dados médicos só são incluídos se `share_medical_info=true`. "
            "Para acessar o prontuário completo, use o endpoint de prontuário com o `elder_profile_id`."
        ),
        parameters=[
            OpenApiParameter(
                name="pk",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="ID do usuário (campo `id` do User).",
                required=True,
            ),
        ],
        responses={
            200: get_success_response_serializer(PublicProfileSerializer),
            401: ERROR_401_UNAUTHORIZED,
            404: ERROR_404_NOT_FOUND,
        },
        examples=[
            OpenApiExample(
                "Perfil de Cuidador",
                value={
                    "success": True,
                    "data": {
                        "id": 7,
                        "full_name": "Carlos Andrade",
                        "role": "CAREGIVER",
                        "avatar": "https://storage.exemplo.com/avatars/7.jpg",
                        "city": "São Paulo",
                        "state": "SP",
                        "elder_profile_id": None,
                        "email": None,
                        "phone": "(11) 97777-5555",
                        "show_links": True,
                        "profile": {
                            "bio": "Cuidador com foco em idosos com Alzheimer.",
                            "experience_years": 5,
                            "is_available": True,
                            "care_types": ["DEMENTIA_CARE", "MEDICATION_SUPPORT"],
                            "city": "São Paulo",
                            "state": "SP",
                        },
                    },
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Perfil de Profissional de Saúde",
                value={
                    "success": True,
                    "data": {
                        "id": 9,
                        "full_name": "Dra. Fernanda Lima",
                        "role": "PROFESSIONAL",
                        "avatar": None,
                        "city": "Rio de Janeiro",
                        "state": "RJ",
                        "elder_profile_id": None,
                        "email": "fernanda@clinica.com",
                        "phone": None,
                        "show_links": False,
                        "profile": {
                            "profession": "PHYSIOTHERAPIST",
                            "profession_other": None,
                            "council": "CREFITO",
                            "license_number": "123456-F",
                            "bio": "Fisioterapeuta especializada em reabilitação geriátrica.",
                            "service_mode": "HOME",
                            "hourly_rate": "150.00",
                            "is_available": True,
                            "city": "Rio de Janeiro",
                            "state": "RJ",
                        },
                    },
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Perfil de Idoso",
                value={
                    "success": True,
                    "data": {
                        "id": 3,
                        "full_name": "Dona Aparecida",
                        "role": "ELDER",
                        "avatar": None,
                        "city": "Campinas",
                        "state": "SP",
                        "elder_profile_id": 2,
                        "email": None,
                        "phone": None,
                        "show_links": True,
                        "profile": {
                            "preferred_name": "Vovó Cida",
                            "share_medical_info": True,
                            "medical_conditions": "Hipertensão",
                            "allergies": None,
                            "medications": "Losartana 50mg",
                        },
                    },
                },
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def get(self, request, pk):
        user = get_object_or_404(User, id=pk, is_active=True)

        avatar_url = None
        if user.avatar:
            try:
                avatar_url = request.build_absolute_uri(user.avatar.url)
            except Exception:
                pass

        profile = {}
        elder_profile_id = None

        if user.role == "ELDER" and hasattr(user, "elder_profile"):
            p = user.elder_profile
            elder_profile_id = p.pk
            profile = {"preferred_name": p.preferred_name or None}
            if p.share_medical_info:
                profile.update({
                    "share_medical_info": True,
                    "medical_conditions": p.medical_conditions or None,
                    "allergies": p.allergies or None,
                    "medications": p.medications or None,
                })

        elif user.role == "CAREGIVER" and hasattr(user, "caregiver_profile"):
            p = user.caregiver_profile
            profile = {
                "bio": p.bio,
                "experience_years": p.experience_years,
                "is_available": p.is_available,
                "care_types": list(p.care_types.values_list("care_type", flat=True)),
                "city": p.city or user.city,
                "state": p.state or user.state,
            }

        elif user.role == "PROFESSIONAL" and hasattr(user, "professional_profile"):
            p = user.professional_profile
            profile = {
                "profession": p.profession,
                "profession_other": p.profession_other or None,
                "council": p.council or None,
                "license_number": p.license_number or None,
                "bio": p.bio,
                "service_mode": p.service_mode,
                "hourly_rate": str(p.hourly_rate) if p.hourly_rate else None,
                "is_available": p.is_available,
                "city": p.city or user.city,
                "state": p.state or user.state,
            }

        elif user.role == "INSTITUTION" and hasattr(user, "institution_profile"):
            p = user.institution_profile
            profile = {
                "legal_name": p.legal_name,
                "trade_name": p.trade_name,
                "institution_type": p.institution_type,
                "capacity": p.capacity,
                "website": p.website,
            }

        elif user.role == "GUARDIAN" and hasattr(user, "guardian_profile"):
            p = user.guardian_profile
            profile = {
                "relationship": p.relationship,
                "is_legal_guardian": p.is_legal_guardian,
            }

        return success_response(data={
            "id": user.id,
            "full_name": user.full_name,
            "role": user.role,
            "avatar": avatar_url,
            "city": user.city or None,
            "state": user.state or None,
            "elder_profile_id": elder_profile_id,
            "profile": profile,
            "email": user.email if user.show_email else None,
            "phone": user.phone if user.show_phone and user.phone else None,
            "show_links": user.show_links,
        })
