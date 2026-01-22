from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient


def test_health_check_returns_ok():
    """
    Verifica se o endpoint de health check responde 200 e retorna status ok.
    """
    client = APIClient()

    url = reverse("health-check")
    response = client.get(url)

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "data": {"status": "ok", "message": "API de rede de cuidados ativa"},
    }
