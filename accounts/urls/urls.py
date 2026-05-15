from django.urls import path
from ..views.verify_email import VerifyEmailView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from ..views import (
    TokenByEmailView, 
    MeView, 
    SignupView,
    ElderMeView,
    CaregiverMeView,
    ProfessionalMeView,
    InstitutionMeView,
)
from ..views.password import ChangePasswordView

urlpatterns = [
    path("token/", TokenByEmailView.as_view(), name="token_by_email"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("signup/", SignupView.as_view(), name="auth-signup"),
    path("password/change/", ChangePasswordView.as_view(), name="change-password"),
    
    # Profile specific "me" routes
    path("elder/me/", ElderMeView.as_view(), name="elder-me"),
    path("caregiver/me/", CaregiverMeView.as_view(), name="caregiver-me"),
    path("professional/me/", ProfessionalMeView.as_view(), name="professional-me"),
    path("institution/me/", InstitutionMeView.as_view(), name="institution-me"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
]
