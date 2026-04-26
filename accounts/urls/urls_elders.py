from django.urls import path
from ..views import ElderMeView, ElderMedicalRecordView

urlpatterns = [
    path("me/", ElderMeView.as_view(), name="elder-me"),
    path("<int:pk>/medical-record/", ElderMedicalRecordView.as_view(), name="elder-medical-record"),
]
