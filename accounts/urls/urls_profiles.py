from django.urls import path
from ..views import (
    ElderMeView,
    CaregiverMeView,
    ProfessionalMeView,
    InstitutionMeView,
)

# We define a single pattern "me/" that can be regularized if needed,
# but since they belong to different prefixes in backend/urls.py,
# we need separate entries or a modular approach.

# To handle prefixes like /api/v1/caregivers/me/, we use:
# path("me/", ...),

def profile_me_url(view_class, name):
    return [path("me/", view_class.as_view(), name=name)]

urlpatterns_elder = profile_me_url(ElderMeView, "elder-me")
urlpatterns_caregiver = profile_me_url(CaregiverMeView, "caregiver-me")
urlpatterns_professional = profile_me_url(ProfessionalMeView, "professional-me")
urlpatterns_institution = profile_me_url(InstitutionMeView, "institution-me")
