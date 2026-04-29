from rest_framework import permissions, status
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from core.pagination import CommentCursorPagination, FeedPagePagination
from core.exceptions.responses import success_response
from posts.docs.post_endpoints import (
    schema_posts_comment_create,
    schema_posts_comment_delete,
    schema_posts_comment_list,
    schema_posts_comment_update,
)
from posts.selectors.post_comment_selectors import get_post_comments_queryset
from posts.serializers.post_comment_serializers import (
    PostCommentCreateSerializer,
    PostCommentListSerializer,
    PostCommentResponseSerializer,
    PostCommentUpdateSerializer,
)
from posts.services.post_comment_services import (
    create_post_comment,
    delete_post_comment,
    update_post_comment,
)


class PostCommentListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser]

    def _get_paginator(self, request):
        if "page" in request.query_params:
            return FeedPagePagination()
        return CommentCursorPagination()

    @schema_posts_comment_list()
    def get(self, request, post_id: int, *args, **kwargs):
        queryset = get_post_comments_queryset(post_id=post_id)
        paginator = self._get_paginator(request)
        page = paginator.paginate_queryset(queryset, request, view=self)

        serializer = PostCommentListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @schema_posts_comment_create()
    def post(self, request, post_id: int, *args, **kwargs):
        serializer = PostCommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        post_comment = create_post_comment(
            actor=request.user,
            post_id=post_id,
            content=serializer.validated_data["content"],
        )

        response_serializer = PostCommentResponseSerializer(
            instance={
                "id": post_comment.id,
                "post_id": post_comment.post_id,
                "user": request.user.id,
                "user_id": request.user.id,
                "content": post_comment.content,
                "comments_count": post_comment.post.comments_count,
                "created_at": post_comment.created_at,
                "updated_at": post_comment.updated_at,
            }
        )
        return success_response(data=response_serializer.data, status_code=status.HTTP_201_CREATED)


class PostCommentDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [JSONParser]

    @schema_posts_comment_update()
    def patch(self, request, post_id: int, comment_id: int, *args, **kwargs):
        serializer = PostCommentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        post_comment = update_post_comment(
            actor=request.user,
            post_id=post_id,
            comment_id=comment_id,
            content=serializer.validated_data["content"],
        )

        response_serializer = PostCommentResponseSerializer(
            instance={
                "id": post_comment.id,
                "post_id": post_comment.post_id,
                "user": post_comment.user_id,
                "user_id": post_comment.user_id,
                "content": post_comment.content,
                "comments_count": post_comment.post.comments_count,
                "created_at": post_comment.created_at,
                "updated_at": post_comment.updated_at,
            }
        )
        return success_response(data=response_serializer.data)

    @schema_posts_comment_delete()
    def delete(self, request, post_id: int, comment_id: int, *args, **kwargs):
        delete_post_comment(
            actor=request.user,
            post_id=post_id,
            comment_id=comment_id,
        )
        return Response(status=status.HTTP_204_NO_CONTENT)
