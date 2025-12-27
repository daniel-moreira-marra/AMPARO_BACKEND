from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class TokenByEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs["email"]
        password = attrs["password"]

        user = authenticate(self.context["request"], email=email, password=password)
        if not user:
            # mensagem genérica: evita vazamento de info
            raise serializers.ValidationError("Credenciais inválidas.")

        if not user.is_active:
            raise serializers.ValidationError("Usuário desativado.")

        refresh = RefreshToken.for_user(user)
        return {"refresh": str(refresh), "access": str(refresh.access_token)}
