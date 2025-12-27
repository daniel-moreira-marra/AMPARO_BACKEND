from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ..docs import me_docs

from ..serializers import MeSerializer

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @me_docs()
    def get(self, request):
        return Response(MeSerializer(request.user).data)