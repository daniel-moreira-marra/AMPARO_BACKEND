from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()

class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "full_name", "phone", "role", "is_verified")
        read_only_fields = fields
