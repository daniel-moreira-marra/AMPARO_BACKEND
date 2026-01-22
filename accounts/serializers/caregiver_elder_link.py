from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from ..models import ElderProfile, CaregiverElderLink


class CaregiverElderLinkSerializer(serializers.ModelSerializer):
    """
    Serializer do vínculo Caregiver ↔ Elder.

    Segurança:
    - caregiver é read_only e vem do usuário logado (CaregiverProfile).
    """

    caregiver = serializers.PrimaryKeyRelatedField(read_only=True)
    elder = serializers.PrimaryKeyRelatedField(queryset=ElderProfile.objects.all())

    class Meta:
        model = CaregiverElderLink
        fields = (
            "id",
            "caregiver",
            "elder",
            "status",
            "started_at",
            "ended_at",
            "agreed_hourly_rate",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "caregiver")

    def _get_caregiver_profile(self):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        profile = getattr(user, "caregiver_profile", None)
        
        if profile is None:
            raise PermissionDenied("Usuário não possui CaregiverProfile.")
        return profile

    def validate(self, attrs):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return attrs

        caregiver_profile = self._get_caregiver_profile()

        elder = attrs.get("elder") or getattr(self.instance, "elder", None)
        is_active = attrs.get("is_active", getattr(self.instance, "is_active", True))

        started_at = attrs.get("started_at", getattr(self.instance, "started_at", None))
        ended_at = attrs.get("ended_at", getattr(self.instance, "ended_at", None))
        if started_at and ended_at and ended_at < started_at:
            raise serializers.ValidationError({"ended_at": "A data de fim não pode ser anterior ao início."})

        if elder and is_active:
            qs = CaregiverElderLink.objects.filter(
                caregiver=caregiver_profile,
                elder=elder,
                is_active=True,
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"elder": "Já existe um vínculo ativo com este idoso."})

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        caregiver_profile = self._get_caregiver_profile()
        return CaregiverElderLink.objects.create(
            caregiver=caregiver_profile,
            **validated_data,
        )

    @transaction.atomic
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
