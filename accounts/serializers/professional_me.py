from rest_framework import serializers
from ..models import ProfessionalProfile


class ProfessionalMeSerializer(serializers.ModelSerializer):
    """
    Atualização do próprio perfil profissional.
    """

    class Meta:
        model = ProfessionalProfile
        fields = (
            "profession",
            "profession_other",
            "council",
            "license_number",
            "bio",
            "service_mode",
            "hourly_rate",
            "is_available",
            "registration_verified",
            "city",
            "state",
        )
        read_only_fields = (
            "registration_verified",
        )
