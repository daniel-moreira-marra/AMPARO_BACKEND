from django.urls import path
from accounts.views.professional_me import ProfessionalMeView

urlpatterns = [
    path("me/", ProfessionalMeView.as_view(), name="professional-me"),
]
