from django.db import transaction
from rest_framework import serializers

from ..models import ElderProfile, GuardianElderLink, GuardianProfile


class GuardianElderLinkSerializer(serializers.ModelSerializer):
    """
    Serializer do vínculo entre Guardian e Elder.

    Segurança:
    - guardian é read_only e vem do usuário logado.
    """

    guardian = serializers.PrimaryKeyRelatedField(read_only=True)
    elder = serializers.PrimaryKeyRelatedField(queryset=ElderProfile.objects.all())

    class Meta:
        model = GuardianElderLink
        fields = (
            "id",
            "guardian",
            "elder",
            "relationship",
            "is_legal_guardian",
            "can_view_medical",
            "can_hire",
            "is_active",
            "created_at",
        )
        read_only_fields = ("id", "created_at", "guardian")

    def validate(self, attrs):
        """
        Evita que um Guardian crie dois vínculos ativos com o mesmo Elder
        (se essa regra fizer sentido no seu domínio).
        """
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return attrs

        guardian_profile = getattr(request.user, "guardian_profile", None)
        if guardian_profile is None:
            raise serializers.ValidationError({"detail": "Usuário não possui GuardianProfile."})

        elder = attrs.get("elder") or getattr(self.instance, "elder", None)
        is_active = attrs.get("is_active", getattr(self.instance, "is_active", True))

        # Se estiver criando/ativando, checa duplicidade ativa
        if elder and is_active:
            qs = GuardianElderLink.objects.filter(guardian=guardian_profile, elder=elder, is_active=True)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({"elder": "Já existe um vínculo ativo com este idoso."})

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        request = self.context["request"]
        guardian_profile = request.user.guardian_profile  # garantido pela view
        return GuardianElderLink.objects.create(guardian=guardian_profile, **validated_data)

    @transaction.atomic
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
