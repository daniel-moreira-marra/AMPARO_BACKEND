from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "phone",
            "avatar",
            "role",
            "is_verified",
            "onboarding_completed",
            "show_email",
            "show_phone",
            "show_links",
            "address_line",
            "city",
            "state",
            "zip_code",
        )
        read_only_fields = fields
