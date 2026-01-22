from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from ..models import ElderProfile, ProfessionalElderLink


class ProfessionalElderLinkSerializer(serializers.ModelSerializer):
    """
    Serializer do vínculo Professional ↔ Elder.

    Segurança:
    - professional é read_only e vem do usuário logado (ProfessionalProfile).
    """

    professional = serializers.PrimaryKeyRelatedField(read_only=True)
    elder = serializers.PrimaryKeyRelatedField(queryset=ElderProfile.objects.all())

    class Meta:
        model = ProfessionalElderLink
        fields = (
            "id",
            "professional",
            "elder",
            "status",
            "started_at",
            "ended_at",
            "agreed_hourly_rate",
            "service_mode",
            "goals",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "professional")

    def _get_professional_profile(self):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        
        professional_profile = getattr(user, "professional_profile", None)
        if professional_profile is None:
            raise PermissionDenied("Usuário não possui ProfessionalProfile.")
        return professional_profile

    def validate(self, attrs):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return attrs

        professional_profile = self._get_professional_profile()

        elder = attrs.get("elder") or getattr(self.instance, "elder", None)
        is_active = attrs.get("is_active", getattr(self.instance, "is_active", True))

        started_at = attrs.get("started_at", getattr(self.instance, "started_at", None))
        ended_at = attrs.get("ended_at", getattr(self.instance, "ended_at", None))
        if started_at and ended_at and ended_at < started_at:
            raise serializers.ValidationError({"ended_at": "A data de fim não pode ser anterior ao início."})

        if elder and is_active:
            qs = ProfessionalElderLink.objects.filter(
                professional=professional_profile,
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
        professional_profile = self._get_professional_profile()
        return ProfessionalElderLink.objects.create(
            professional=professional_profile,
            **validated_data,
        )

    @transaction.atomic
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
