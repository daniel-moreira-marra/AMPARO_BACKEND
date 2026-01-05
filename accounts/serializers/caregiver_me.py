from django.db import transaction
from rest_framework import serializers

from ..models import CaregiverProfile, CaregiverCareType
from ..models.enums import CareType


class CaregiverMeSerializer(serializers.ModelSerializer):
    """
    Atualização do próprio perfil de cuidador.
    Inclui care_types como lista de strings (múltiplos).
    """
    care_types = serializers.ListField(
        child=serializers.ChoiceField(choices=CareType.choices),
        required=False,
        help_text="Lista de tipos de atendimento que o cuidador realiza.",
    )

    class Meta:
        model = CaregiverProfile
        fields = (
            "bio",
            "experience_years",
            "is_available",
            "city",
            "state",
            "care_types",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["care_types"] = list(
            instance.care_types.values_list("care_type", flat=True)
        )
        return data

    @transaction.atomic
    def update(self, instance, validated_data):
        care_types = validated_data.pop("care_types", None)

        # Atualiza campos do profile
        instance = super().update(instance, validated_data)

        # Se care_types veio no payload, sincroniza os registros
        if care_types is not None:
            CaregiverCareType.objects.filter(caregiver=instance).exclude(
                care_type__in=care_types
            ).delete()

            existing = set(
                CaregiverCareType.objects.filter(caregiver=instance).values_list("care_type", flat=True)
            )
            to_create = [ct for ct in care_types if ct not in existing]
            CaregiverCareType.objects.bulk_create(
                [CaregiverCareType(caregiver=instance, care_type=ct) for ct in to_create]
            )

        return instance
