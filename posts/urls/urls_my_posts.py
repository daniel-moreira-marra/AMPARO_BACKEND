from django.urls import path

from posts.views.post_views import MyPostsViewSet

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
]
