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
    phone = serializers.CharField(max_length=30, required=False, allow_blank=True)
    role = serializers.ChoiceField(choices=UserRole.choices)

    def validate_email(self, value: str) -> str:
        email = value.strip().lower()
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Este e-mail já está em uso.")
        return email

    def validate_password(self, value: str) -> str:
        # Usa os validadores de senha do Django (boa prática)
        password_validation.validate_password(value)
        return value

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            **validated_data,
        )

        # Por enquanto, só existe o profile de idoso
        if getattr(user, "role", None) == "ELDER":
            ElderProfile.objects.create(user=user)
        elif getattr(user, "role", None) == "CAREGIVER":
            CaregiverProfile.objects.create(user=user)
        elif getattr(user, "role", None) == "GUARDIAN":
            GuardianProfile.objects.create(user=user)
        elif getattr(user, "role", None) == "INSTITUTION":
            InstitutionProfile.objects.create(user=user)
        elif getattr(user, "role", None) == "PROFESSIONAL":
            ProfessionalProfile.objects.create(user=user)
        elif getattr(user, "role", None) is None:
            raise serializers.ValidationError("O campo 'role' é obrigatório.")

        return user


class SignupResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "full_name", "phone", "role")
        read_only_fields = fields
