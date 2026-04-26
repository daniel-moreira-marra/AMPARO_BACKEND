from django.urls import path

from ..views.public_user import PublicUserView
from posts.views.user_posts_view import UserPostsView

urlpatterns = [
    path("<int:pk>/", PublicUserView.as_view(), name="public-user"),
    path("<int:pk>/posts/", UserPostsView.as_view(), name="user-posts"),
]
