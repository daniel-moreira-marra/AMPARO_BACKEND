from django.urls import path

from accounts.views.institution_me import InstitutionMeView
from accounts.views.institution_elder_link import InstitutionElderLinkViewSet

institution_elder_links = InstitutionElderLinkViewSet.as_view({
    "get": "list",
    "post": "create",
})

institution_elder_link_detail = InstitutionElderLinkViewSet.as_view({
    "get": "retrieve",
    "put": "update",
    "patch": "partial_update",
    "delete": "destroy",
})

urlpatterns = [
    # Perfil da instituição
    path("me/", InstitutionMeView.as_view(), name="institution-me"),

    # Vínculos com idosos
    path(
        "me/link-to-elder/",
        institution_elder_links,
        name="institution-me-elder-links",
    ),
    path(
        "me/link-to-elder/<int:pk>/",
        institution_elder_link_detail,
        name="institution-me-elder-link-detail",
    ),
]
