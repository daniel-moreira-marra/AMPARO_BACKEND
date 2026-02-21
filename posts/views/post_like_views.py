from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.exceptions.responses import success_response
from posts.docs.post_endpoints import schema_posts_like_create, schema_posts_unlike_delete
from posts.serializers.post_serializers import PostLikeResponseSerializer
from posts.services.post_like_services import like_post, unlike_post


class PostLikeCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @schema_posts_like_create()
    def post(self, request, post_id: int, *args, **kwargs):
        post_like = like_post(actor=request.user, post_id=post_id)

        serializer = PostLikeResponseSerializer(
            instance={
                "id": post_like.id,
                "post_id": post_like.post_id,
                "user_id": request.user.id,
                "likes_count": post_like.post.likes_count,
                "created_at": post_like.created_at,
            }
        )
        return success_response(data=serializer.data, status_code=status.HTTP_201_CREATED)


class PostUnlikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @schema_posts_unlike_delete()
    def delete(self, request, post_id: int, *args, **kwargs):
        unlike_post(actor=request.user, post_id=post_id)
        return Response(status=status.HTTP_204_NO_CONTENT)
