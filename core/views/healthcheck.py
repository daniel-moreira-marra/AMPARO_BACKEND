from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response

from core.docs import healthcheck_docs

class HealthCheckView(APIView):
    """
    Endpoint simples para o frontend testar se a API está ativa.
    Não exige autenticação.
    """
    @healthcheck_docs()
    def get(self, request):
        # Pode retornar também versão da API, status, etc.
        return Response({"status": "ok", "message": "API de rede de cuidados ativa"})
