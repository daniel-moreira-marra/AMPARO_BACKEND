from rest_framework import serializers
from ..models import GuardianProfile


class GuardianMeSerializer(serializers.ModelSerializer):
    """
    Atualização do próprio perfil de responsável (GUARDIAN).
    """

    class Meta:
        model = GuardianProfile
        fields = (
            "relationship",
            "is_legal_guardian",
            "preferred_contact",
        )
