from rest_framework import serializers
from ..models import Post


def _get_images(obj) -> list[str]:
    """Return image URLs for a Post, preferring PostImage records over the legacy image field."""
    post_images = obj.post_images.all()
    if post_images:
        return [pi.image.url for pi in post_images if pi.image]
    if obj.image:
        return [obj.image.url]
    return []


class SharedPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.full_name", read_only=True)
    author_id = serializers.IntegerField(source="author.id", read_only=True)
    images = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "author_id",
            "author_name",
            "author_role",
            "text",
            "image",
            "image_alt_text",
            "images",
            "created_at",
        )
        read_only_fields = fields

    def get_images(self, obj) -> list[str]:
        return _get_images(obj)


class FeedPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.full_name", read_only=True)
    author_id = serializers.IntegerField(source="author.id", read_only=True)
    author_avatar = serializers.SerializerMethodField()
    liked_by_me = serializers.SerializerMethodField()
    shared_post = SharedPostSerializer(source="parent_post", read_only=True)
    images = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "author_id",
            "author_name",
            "author_avatar",
            "author_role",
            "text",
            "image",
            "image_alt_text",
            "images",
            "tags",
            "likes_count",
            "comments_count",
            "liked_by_me",
            "shared_post",
            "created_at",
            "published_at",
        )
        read_only_fields = fields

    def get_author_avatar(self, obj) -> str | None:
        if obj.author.avatar:
            return obj.author.avatar.url
        return None

    def get_liked_by_me(self, obj) -> bool:
        return getattr(obj, "_liked_by_me", False)

    def get_images(self, obj) -> list[str]:
        return _get_images(obj)
