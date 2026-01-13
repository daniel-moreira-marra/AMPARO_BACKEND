from rest_framework import serializers
from ..models import InstitutionProfile


class InstitutionMeSerializer(serializers.ModelSerializer):
    """
    Atualização do próprio perfil de instituição.
    """

    class Meta:
        model = InstitutionProfile
        fields = (
            "legal_name",
            "trade_name",
            "cnpj",
            "institution_type",
            "capacity",
            "website",
            "address_line",
            "city",
            "state",
            "zip_code",
            "license_number",
            "is_verified",
        )
        # Em geral, verificação é controlada pelo sistema/admin
        read_only_fields = ("is_verified",)
