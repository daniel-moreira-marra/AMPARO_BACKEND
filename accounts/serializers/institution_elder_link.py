from django.db import transaction
from rest_framework import serializers

from ..models import ElderProfile, InstitutionElderLink


from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from ..models import ElderProfile, InstitutionElderLink

from core.exceptions.helpers import deny_role


class InstitutionElderLinkSerializer(serializers.ModelSerializer):
    """
    Serializer do vínculo Institution ↔ Elder.

    Segurança:
    - institution é read_only e vem do usuário logado (InstitutionProfile).
    """

    institution = serializers.PrimaryKeyRelatedField(read_only=True)
    elder = serializers.PrimaryKeyRelatedField(queryset=ElderProfile.objects.all())

    class Meta:
        model = InstitutionElderLink
        fields = (
            "id",
            "institution",
            "elder",
            "status",
            "admitted_at",
            "discharged_at",
            "room",
            "bed",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at", "institution")

    def _get_institution_profile(self):
        """
        Retorna o InstitutionProfile do usuário logado, ou lança 403.
        """
        request = self.context.get("request")
        user = getattr(request, "user", None)

        institution_profile = getattr(user, "institution_profile", None)
        if institution_profile is None:
            # Isso é permissão/escopo, não validação de payload
            raise PermissionDenied("Usuário não possui InstitutionProfile.")

        return institution_profile

    def validate(self, attrs):
        """
        Regras úteis:
        - impede vínculo ativo duplicado (institution+elder) se is_active=True
        - discharged_at não deve ser anterior a admitted_at (quando ambos existem)
        """
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return attrs

        institution_profile = self._get_institution_profile()

        elder = attrs.get("elder") or getattr(self.instance, "elder", None)
        is_active = attrs.get("is_active", getattr(self.instance, "is_active", True))

        admitted_at = attrs.get("admitted_at", getattr(self.instance, "admitted_at", None))
        discharged_at = attrs.get("discharged_at", getattr(self.instance, "discharged_at", None))
        if admitted_at and discharged_at and discharged_at < admitted_at:
            raise serializers.ValidationError(
                {"discharged_at": "A data de saída não pode ser anterior à admissão."}
            )

        if elder and is_active:
            qs = InstitutionElderLink.objects.filter(
                institution=institution_profile,
                elder=elder,
                is_active=True,
            )
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {"elder": "Já existe um vínculo ativo com este idoso."}
                )

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """
        Institution vem sempre do usuário logado.
        """
        institution_profile = self._get_institution_profile()
        return InstitutionElderLink.objects.create(
            institution=institution_profile,
            **validated_data,
        )

    @transaction.atomic
    def update(self, instance, validated_data):
        # Não precisa recalcular institution aqui; ela é read_only
        return super().update(instance, validated_data)
