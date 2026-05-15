from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from ..views import TokenByEmailView, SignupView, MeView, CompleteOnboardingView
from ..views.password import ChangePasswordView

urlpatterns = [
    path("token/", TokenByEmailView.as_view(), name="token_by_email"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("signup/", SignupView.as_view(), name="auth-signup"),
    path("me/", MeView.as_view(), name="me"),
    path("password/change/", ChangePasswordView.as_view(), name="change-password"),
    path("onboarding/complete/", CompleteOnboardingView.as_view(), name="onboarding-complete"),
    path("verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path("password-reset/", PasswordResetRequestView.as_view(), name="password-reset-request"),
    path("password-reset/confirm/", PasswordResetConfirmView.as_view(), name="password-reset-confirm"),
]
