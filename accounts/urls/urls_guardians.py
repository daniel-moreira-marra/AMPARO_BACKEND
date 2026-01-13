from django.urls import path

from ..views.guardian_elder_link import GuardianElderLinkViewSet

urlpatterns = [
    path("link-to-elder/", GuardianElderLinkViewSet.as_view({'get': 'list', 'post': 'create'}), name="link_to_elder"),
]
