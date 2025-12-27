from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from ..views import TokenByEmailView, MeView, SignupView
urlpatterns = [
    path("token/", TokenByEmailView.as_view(), name="token_by_email"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("signup/", SignupView.as_view(), name="auth-signup"),
]
