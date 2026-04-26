from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UpdateMeSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(max_length=40, required=False, allow_blank=True)
    state = serializers.CharField(max_length=10, required=False, allow_blank=True)
    zip_code = serializers.CharField(max_length=20, required=False, allow_blank=True)
    avatar = serializers.ImageField(required=False, allow_null=True)

    show_email = serializers.BooleanField(required=False)
    show_phone = serializers.BooleanField(required=False)
    show_links = serializers.BooleanField(required=False)

    class Meta:
        model = User
        fields = ("full_name", "phone", "address_line", "city", "state", "zip_code", "avatar", "show_email", "show_phone", "show_links")


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
