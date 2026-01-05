from django.urls import path
from ..views import ElderMeView

urlpatterns = [
    path("me/", ElderMeView.as_view(), name="elder-me"),
]
