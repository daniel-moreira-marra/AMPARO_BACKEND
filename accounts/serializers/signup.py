from django.contrib.auth import get_user_model, password_validation
from django.db import transaction
from rest_framework import serializers

from ..models import UserRole, ElderProfile, CaregiverProfile, GuardianProfile, InstitutionProfile, ProfessionalProfile  # ajuste se seu import estiver diferente

User = get_user_model()


class SignupSerializer(serializers.Serializer):
    """
    Cadastro básico de usuário.
    - Cria User.
    - Se role == ELDER, cria ElderProfile (por enquanto é o único profile existente).
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    full_name = serializers.CharField(max_length=150)
    phone = serializers.CharField(max_length=40, required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=UserRole.choices)
    address_line = serializers.CharField(max_length=255, required=False, allow_blank=True)
    city = serializers.CharField(max_length=120, required=False, allow_blank=True)
    state = serializers.CharField(max_length=10, required=False, allow_blank=True)
    zip_code = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_email(self, value: str) -> str:
        email = value.strip().lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Este e-mail já está em uso.")
        return email

    def validate_password(self, value: str) -> str:
        # Usa os validadores de senha do Django (boa prática)
        password_validation.validate_password(value)
        return value

    def validate(self, attrs):
        role = attrs.get("role")
        if role == UserRole.INSTITUTION:
            missing_fields = []
            for field in ("address_line", "city", "state", "zip_code"):
                value = attrs.get(field, "")
                if not str(value).strip():
                    missing_fields.append(field)
            if missing_fields:
                raise serializers.ValidationError(
                    {field: "Este campo é obrigatório para INSTITUTION." for field in missing_fields}
                )
        return attrs


class SignupResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "full_name", "phone", "role", "address_line", "city", "state", "zip_code")
        read_only_fields = fields
