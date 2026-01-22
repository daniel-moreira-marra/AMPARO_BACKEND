from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from ..docs import me_docs

from ..serializers import MeSerializer
from core.exceptions.responses import success_response

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @me_docs()
    def get(self, request):
        return success_response(data=MeSerializer(request.user).data)
