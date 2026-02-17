from django.urls import path
from ..views import ProfessionalMeView

urlpatterns = [
    path("me/", ProfessionalMeView.as_view(), name="professional-me"),
]
