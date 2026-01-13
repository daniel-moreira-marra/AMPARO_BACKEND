from django.urls import path

from ..views import InstitutionMeView

urlpatterns = [
    path("me/", InstitutionMeView.as_view(), name="institution_me"),
]
