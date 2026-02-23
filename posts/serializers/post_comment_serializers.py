from rest_framework import serializers


class PostCommentContentSerializer(serializers.Serializer):
    content = serializers.CharField(
        required=True,
        trim_whitespace=False,
        help_text="Texto do comentário (máximo de 500 caracteres).",
    )

    def validate_content(self, value: str) -> str:
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("O conteúdo do comentário é obrigatório.")
        if len(value) > 500:
            raise serializers.ValidationError("O comentário deve ter no máximo 500 caracteres.")
        return value


class PostCommentCreateSerializer(PostCommentContentSerializer):
    pass


class PostCommentUpdateSerializer(PostCommentContentSerializer):
    pass


class PostCommentResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    post_id = serializers.IntegerField()
    user = serializers.IntegerField()
    user_id = serializers.IntegerField()
    content = serializers.CharField()
    comments_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class PostCommentListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    post_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    content = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
