from django.urls import path

from posts.views.post_views import MyPostsViewSet
from posts.views.post_like_views import PostLikeCreateView, PostUnlikeView

post_list_create = MyPostsViewSet.as_view({
    "get": "list",
    "post": "create",
})

post_detail = MyPostsViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})

urlpatterns = [
    path("my-posts/", post_list_create, name="my-posts-list-create"),
    path("my-posts/<int:pk>/", post_detail, name="my-posts-detail"),
    path("like/<int:post_id>", PostLikeCreateView.as_view(), name="post-like-create"),
    path("unlike/<int:post_id>", PostUnlikeView.as_view(), name="post-unlike"),
]
