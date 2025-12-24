from django.urls import path
from core.views.healthcheck import HealthCheckView

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health-check'),
]
