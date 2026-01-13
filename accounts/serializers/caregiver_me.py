from django.db import transaction
from rest_framework import serializers

from ..models import CaregiverProfile, CaregiverCareType
from ..models.enums import CareType


class CaregiverMeSerializer(serializers.ModelSerializer):
    """
    Atualização do próprio perfil de cuidador.

    Abordagem 1:
    - care_types (read): devolve a lista de tipos cadastrados para o cuidador
    - care_types_input (write): recebe a lista de tipos para sincronizar no banco
    """

    # ✅ Campo de leitura (não tenta iterar RelatedManager)
    care_types = serializers.SerializerMethodField(
        help_text="Lista de tipos de atendimento que o cuidador realiza."
    )

    # ✅ Campo de escrita (payload de entrada)
    care_types_input = serializers.ListField(
        child=serializers.ChoiceField(choices=CareType.choices),
        required=False,
        write_only=True,
        help_text="Lista de tipos de atendimento para salvar no perfil (substitui o conjunto atual).",
    )

    class Meta:
        model = CaregiverProfile
        fields = (
            "bio",
            "experience_years",
            "is_available",
            "city",
            "state",
            "care_types",        # read
            "care_types_input",  # write
        )

    def get_care_types(self, instance):
        """
        Retorna a lista de care_types cadastrados no relacionamento.
        """
        return list(instance.care_types.values_list("care_type", flat=True))

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Atualiza o profile e, se care_types_input estiver presente, sincroniza os tipos.
        """
        care_types = validated_data.pop("care_types_input", None)

        # Atualiza campos do profile
        instance = super().update(instance, validated_data)

        # Se care_types_input veio no payload, sincroniza os registros
        if care_types is not None:
            # Remove os que não estão mais na lista
            CaregiverCareType.objects.filter(caregiver=instance).exclude(
                care_type__in=care_types
            ).delete()

            # Cria os que faltam (evita duplicar)
            existing = set(
                CaregiverCareType.objects.filter(caregiver=instance).values_list("care_type", flat=True)
            )
            to_create = [ct for ct in care_types if ct not in existing]
            CaregiverCareType.objects.bulk_create(
                [CaregiverCareType(caregiver=instance, care_type=ct) for ct in to_create]
            )

        return instance
