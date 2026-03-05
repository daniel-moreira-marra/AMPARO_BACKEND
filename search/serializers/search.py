from rest_framework import serializers

from accounts.models import (
    ElderProfile,
    GuardianProfile,
    CaregiverProfile,
    ProfessionalProfile,
    InstitutionProfile,
)


class ElderSearchSerializer(serializers.ModelSerializer):
    """
    Serializer de resultado de busca para idosos.
    """
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    role = serializers.SerializerMethodField()

    class Meta:
        model = ElderProfile
        fields = (
            "id",
            "role",
            "full_name",
            "preferred_name",
            "gender",
            "mobility_level",
        )

    def get_role(self, obj):
        return "ELDER"


class GuardianSearchSerializer(serializers.ModelSerializer):
    """
    Serializer de resultado de busca para responsáveis.
    """
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    role = serializers.SerializerMethodField()

    class Meta:
        model = GuardianProfile
        fields = (
            "id",
            "role",
            "full_name",
            "relationship",
            "is_legal_guardian",
        )

    def get_role(self, obj):
        return "GUARDIAN"


class CaregiverSearchSerializer(serializers.ModelSerializer):
    """
    Serializer de resultado de busca para cuidadores.
    """
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    role = serializers.SerializerMethodField()

    class Meta:
        model = CaregiverProfile
        fields = (
            "id",
            "role",
            "full_name",
            "bio",
            "experience_years",
            "city",
            "state",
            "is_available",
        )

    def get_role(self, obj):
        return "CAREGIVER"


class ProfessionalSearchSerializer(serializers.ModelSerializer):
    """
    Serializer de resultado de busca para profissionais de saúde.
    """
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    role = serializers.SerializerMethodField()
    profession_display = serializers.CharField(source="get_profession_display", read_only=True)

    class Meta:
        model = ProfessionalProfile
        fields = (
            "id",
            "role",
            "full_name",
            "profession",
            "profession_display",
            "bio",
            "service_mode",
            "hourly_rate",
            "is_available",
            "registration_verified",
            "city",
            "state",
        )

    def get_role(self, obj):
        return "PROFESSIONAL"


class InstitutionSearchSerializer(serializers.ModelSerializer):
    """
    Serializer de resultado de busca para instituições.
    """
    full_name = serializers.CharField(source="user.full_name", read_only=True)
    city = serializers.CharField(source="user.city", read_only=True)
    state = serializers.CharField(source="user.state", read_only=True)
    role = serializers.SerializerMethodField()

    class Meta:
        model = InstitutionProfile
        fields = (
            "id",
            "role",
            "full_name",
            "legal_name",
            "trade_name",
            "institution_type",
            "city",
            "state",
            "is_verified",
        )

    def get_role(self, obj):
        return "INSTITUTION"
