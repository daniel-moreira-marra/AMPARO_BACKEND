from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from core.exceptions.responses import success_response
from core.docs.schemas import (
    get_success_response_serializer,
    ERROR_401_UNAUTHORIZED,
    ERROR_403_FORBIDDEN,
    ERROR_404_NOT_FOUND,
)
from ..models import ElderProfile
from links.models import (
    CaregiverElderLink,
    GuardianElderLink,
    ProfessionalElderLink,
    InstitutionElderLink,
)

GENDER_LABELS = {
    "MALE": "Masculino",
    "FEMALE": "Feminino",
    "OTHER": "Outro",
    "NOT_INFORMED": "Prefiro não informar",
}
MOBILITY_LABELS = {
    "INDEPENDENT": "Independente",
    "NEEDS_ASSISTANCE": "Precisa de assistência",
    "WHEELCHAIR": "Cadeira de rodas",
    "BEDRIDDEN": "Acamado(a)",
}
COGNITIVE_LABELS = {
    "LUCID": "Lúcido(a)",
    "MILD_IMPAIRMENT": "Comprometimento leve",
    "DEMENTIA": "Demência",
    "NOT_INFORMED": "Prefiro não informar",
}


class MedicalRecordSerializer(serializers.Serializer):
    preferred_name = serializers.CharField(allow_null=True, help_text="Nome preferido do idoso.")
    birth_date = serializers.DateField(allow_null=True, help_text="Data de nascimento (YYYY-MM-DD).")
    gender = serializers.ChoiceField(
        choices=["MALE", "FEMALE", "OTHER", "NOT_INFORMED"],
        allow_null=True,
        help_text="Gênero (código interno).",
    )
    gender_display = serializers.CharField(allow_null=True, help_text="Gênero legível em português.")
    mobility_level = serializers.ChoiceField(
        choices=["INDEPENDENT", "NEEDS_ASSISTANCE", "WHEELCHAIR", "BEDRIDDEN"],
        allow_null=True,
        help_text="Nível de mobilidade (código interno).",
    )
    mobility_display = serializers.CharField(allow_null=True, help_text="Mobilidade legível em português.")
    cognitive_status = serializers.ChoiceField(
        choices=["LUCID", "MILD_IMPAIRMENT", "DEMENTIA", "NOT_INFORMED"],
        allow_null=True,
        help_text="Status cognitivo (código interno).",
    )
    cognitive_display = serializers.CharField(allow_null=True, help_text="Status cognitivo legível em português.")
    has_fall_risk = serializers.BooleanField(help_text="Se o idoso possui risco de queda.")
    needs_medication_support = serializers.BooleanField(help_text="Se precisa de auxílio com medicações.")
    requires_24h_care = serializers.BooleanField(help_text="Se requer cuidados 24 horas.")
    medical_conditions = serializers.CharField(allow_null=True, help_text="Condições médicas diagnosticadas.")
    allergies = serializers.CharField(allow_null=True, help_text="Alergias conhecidas.")
    medications = serializers.CharField(allow_null=True, help_text="Medicações em uso.")
    medical_notes = serializers.CharField(allow_null=True, help_text="Observações médicas adicionais.")
    emergency_contact_name = serializers.CharField(allow_null=True, help_text="Nome do contato de emergência.")
    emergency_contact_phone = serializers.CharField(allow_null=True, help_text="Telefone do contato de emergência.")
    emergency_contact_relationship = serializers.CharField(
        allow_null=True,
        help_text="Relação do contato de emergência com o idoso.",
    )


class ElderMedicalRecordView(APIView):
    """
    Retorna a ficha médica completa de um idoso.
    Só é acessível por usuários com vínculo ATIVO com o idoso.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Idoso"],
        summary="Consultar prontuário do idoso",
        description=(
            "Retorna a ficha médica completa de um idoso identificado pelo `pk` "
            "(**ID do ElderProfile**, não do usuário).\n\n"
            "**Acesso restrito:** apenas usuários com vínculo **ATIVO** com o idoso podem acessar. "
            "Cuidadores, responsáveis, profissionais e instituições vinculados têm acesso.\n\n"
            "**Campos com display:** gênero, mobilidade e status cognitivo retornam tanto "
            "o código interno (ex: `WHEELCHAIR`) quanto o label em português (`Cadeira de rodas`)."
        ),
        parameters=[
            OpenApiParameter(
                name="pk",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="ID do **ElderProfile** (não do User). Retornado em `/accounts/users/<id>/` como `elder_profile_id`.",
                required=True,
            ),
        ],
        responses={
            200: get_success_response_serializer(MedicalRecordSerializer),
            401: ERROR_401_UNAUTHORIZED,
            403: ERROR_403_FORBIDDEN,
            404: ERROR_404_NOT_FOUND,
        },
        examples=[
            OpenApiExample(
                "Prontuário completo",
                value={
                    "success": True,
                    "data": {
                        "preferred_name": "Vovó Maria",
                        "birth_date": "1942-03-15",
                        "gender": "FEMALE",
                        "gender_display": "Feminino",
                        "mobility_level": "NEEDS_ASSISTANCE",
                        "mobility_display": "Precisa de assistência",
                        "cognitive_status": "MILD_IMPAIRMENT",
                        "cognitive_display": "Comprometimento leve",
                        "has_fall_risk": True,
                        "needs_medication_support": True,
                        "requires_24h_care": False,
                        "medical_conditions": "Hipertensão, Diabetes tipo 2",
                        "allergies": "Dipirona",
                        "medications": "Losartana 50mg, Metformina 500mg",
                        "medical_notes": "Prefere caminhadas pela manhã.",
                        "emergency_contact_name": "Ana Silva",
                        "emergency_contact_phone": "(11) 98888-7777",
                        "emergency_contact_relationship": "Filha",
                    },
                },
                response_only=True,
                status_codes=["200"],
            ),
            OpenApiExample(
                "Acesso negado — sem vínculo ativo",
                value={
                    "success": False,
                    "error": {
                        "code": "permission_denied",
                        "message": "Você precisa ter um vínculo ativo com este idoso para acessar a ficha médica.",
                        "details": None,
                    },
                },
                response_only=True,
                status_codes=["403"],
            ),
        ],
    )
    def get(self, request, pk):
        elder = get_object_or_404(ElderProfile, pk=pk)
        user = request.user

        is_linked = (
            CaregiverElderLink.objects.filter(
                elder=elder, caregiver__user=user, status="ACTIVE", is_active=True
            ).exists()
            or GuardianElderLink.objects.filter(
                elder=elder, guardian__user=user, status="ACTIVE", is_active=True
            ).exists()
            or ProfessionalElderLink.objects.filter(
                elder=elder, professional__user=user, status="ACTIVE", is_active=True
            ).exists()
            or InstitutionElderLink.objects.filter(
                elder=elder, institution__user=user, status="ACTIVE", is_active=True
            ).exists()
        )

        if not is_linked:
            raise PermissionDenied(
                "Você precisa ter um vínculo ativo com este idoso para acessar a ficha médica."
            )

        return success_response(data={
            "preferred_name": elder.preferred_name or None,
            "birth_date": str(elder.birth_date) if elder.birth_date else None,
            "gender": elder.gender,
            "gender_display": GENDER_LABELS.get(elder.gender, elder.gender),
            "mobility_level": elder.mobility_level,
            "mobility_display": MOBILITY_LABELS.get(elder.mobility_level, elder.mobility_level),
            "cognitive_status": elder.cognitive_status,
            "cognitive_display": COGNITIVE_LABELS.get(elder.cognitive_status, elder.cognitive_status),
            "has_fall_risk": elder.has_fall_risk,
            "needs_medication_support": elder.needs_medication_support,
            "requires_24h_care": elder.requires_24h_care,
            "medical_conditions": elder.medical_conditions or None,
            "allergies": elder.allergies or None,
            "medications": elder.medications or None,
            "medical_notes": elder.medical_notes or None,
            "emergency_contact_name": elder.emergency_contact_name or None,
            "emergency_contact_phone": elder.emergency_contact_phone or None,
            "emergency_contact_relationship": elder.emergency_contact_relationship or None,
        })
