from django.urls import path
from accounts.views import ProfessionalMeView
from accounts.views import ProfessionalElderLinkViewSet

professional_elder_links = ProfessionalElderLinkViewSet.as_view({
    "get": "list",
    "post": "create",
})

professional_elder_link_detail = ProfessionalElderLinkViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})

urlpatterns = [
    path("me/", ProfessionalMeView.as_view(), name="professional-me"),

    path("me/link-to-elder/", professional_elder_links, name="professional-me-elder-links"),
    path("me/link-to-elder/<int:pk>/", professional_elder_link_detail, name="professional-me-elder-link-detail"),
]

