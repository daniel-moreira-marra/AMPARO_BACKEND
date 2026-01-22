from rest_framework.views import APIView

from core.docs import healthcheck_docs
from core.exceptions.responses import success_response

class HealthCheckView(APIView):
    """
    Endpoint simples para o frontend testar se a API está ativa.
    Não exige autenticação.
    """
    @healthcheck_docs()
    def get(self, request):
        # Pode retornar também versão da API, status, etc.
        return success_response(
            data={"status": "ok", "message": "API de rede de cuidados ativa"}
        )
