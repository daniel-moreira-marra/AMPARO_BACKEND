from django.urls import path
from ..views import CaregiverMeView

urlpatterns = [
    path("me/", CaregiverMeView.as_view(), name="caregiver-me"),
]
