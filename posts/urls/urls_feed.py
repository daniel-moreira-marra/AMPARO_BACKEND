from django.urls import path
from ..views.feed_views import FeedListView

urlpatterns = [
    path("feed/", FeedListView.as_view(), name="posts-feed"),
]
