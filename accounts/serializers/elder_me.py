from rest_framework import serializers
from ..models import ElderProfile


class ElderMeSerializer(serializers.ModelSerializer):
    """
    Serializer para o próprio idoso atualizar seu perfil.
    """
    class Meta:
        model = ElderProfile
        fields = (
            "preferred_name",
            "birth_date",
            "gender",
            "mobility_level",
            "cognitive_status",
            "has_fall_risk",
            "needs_medication_support",
            "requires_24h_care",
            "medical_conditions",
            "allergies",
            "medications",
            "medical_notes",
            "emergency_contact_name",
            "emergency_contact_phone",
            "emergency_contact_relationship",
            "share_medical_info",
            "is_active",
        )
