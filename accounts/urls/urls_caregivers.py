from django.urls import path
from ..views import CaregiverMeView

from ..views import CaregiverElderLinkViewSet

caregiver_link_to_elder = CaregiverElderLinkViewSet.as_view({
    "get": "list",
    "post": "create",
})

caregiver_link_to_elder_detail = CaregiverElderLinkViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})


urlpatterns = [
    path("me/", CaregiverMeView.as_view(), name="caregiver-me"),

    path("me/link-to-elder/", caregiver_link_to_elder, name="caregiver-me-elder-links"),
    path("me/link-to-elder/<int:pk>/", caregiver_link_to_elder_detail, name="caregiver-me-elder-link-detail"),
]
