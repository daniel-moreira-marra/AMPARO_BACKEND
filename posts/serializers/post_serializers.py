from django.utils import timezone
from rest_framework import serializers

from posts.models import Post
from posts.enums.post_status import PostStatus
from posts.enums.visibility_scope import VisibilityScope


class PostListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "text",
            "image",
            "image_alt_text",
            "status",
            "visibility_scope",
            "likes_count",
            "comments_count",
            "created_at",
            "updated_at",
            "published_at",
            "edited_at",
        )
        read_only_fields = fields


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "text",
            "image",
            "image_alt_text",
            "status",
            "visibility_scope",
            "parent_post",
        )
        read_only_fields = ("id",)

    def validate_text(self, value: str) -> str:
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("O texto é obrigatório.")
        return value

    def validate(self, attrs: dict) -> dict:
        # Exemplo: se tiver imagem, recomenda alt_text (não obrigatório)
        image = attrs.get("image")
        alt = (attrs.get("image_alt_text") or "").strip()
        if image and not alt:
            # Não bloqueia, só dá um caminho caso você queira tornar obrigatório no futuro
            pass
        return attrs

    def create(self, validated_data: dict) -> Post:
        request = self.context["request"]
        user = request.user

        # Snapshot do papel no momento do post (se existir no seu User)
        author_role = getattr(user, "role", "") or ""

        now = timezone.now()
        status = validated_data.get("status", PostStatus.DRAFT)

        post = Post.objects.create(
            author=user,
            author_role=author_role,
            **validated_data,
        )

        # published_at consistente
        if status == PostStatus.PUBLISHED and not post.published_at:
            post.published_at = now
            post.save(update_fields=["published_at"])

        return post


class PostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "text",
            "image",
            "image_alt_text",
            "status",
            "visibility_scope",
        )

    def validate_text(self, value: str) -> str:
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("O texto é obrigatório.")
        return value

    def update(self, instance: Post, validated_data: dict) -> Post:
        from django.utils import timezone

        now = timezone.now()
        old_status = instance.status

        for field, value in validated_data.items():
            setattr(instance, field, value)

        # Controle de edição / publicação
        instance.edited_at = now

        if old_status != PostStatus.PUBLISHED and instance.status == PostStatus.PUBLISHED:
            instance.published_at = instance.published_at or now

        instance.save()
        return instance
