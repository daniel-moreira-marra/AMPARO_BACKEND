from rest_framework import serializers
from ..models import Post


class FeedPostSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.full_name", read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "author_name",
            "text",
            "image",
            "image_alt_text",
            "likes_count",
            "comments_count",
            "created_at",
            "published_at",
        )
        read_only_fields = fields
