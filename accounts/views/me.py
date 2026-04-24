from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from ..docs import me_docs

from ..serializers import MeSerializer, UpdateMeSerializer
from ..services.user_services import update_user_profile
from core.exceptions.responses import success_response

class MeView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @me_docs()
    def get(self, request):
        return success_response(data=MeSerializer(request.user).data)

    def patch(self, request):
        serializer = UpdateMeSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        user = update_user_profile(user=request.user, data=serializer.validated_data)
        return success_response(data=MeSerializer(user).data)
