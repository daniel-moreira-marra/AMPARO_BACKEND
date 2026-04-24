from django.urls import path
from ..views.public_user import PublicUserView

urlpatterns = [
    path("<int:pk>/", PublicUserView.as_view(), name="public-user"),
]
