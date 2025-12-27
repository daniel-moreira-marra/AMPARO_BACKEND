from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from drf_spectacular.utils import extend_schema

from ..serializers import TokenByEmailSerializer

from ..docs import token_by_email_docs

class TokenByEmailView(APIView):
    permission_classes = [AllowAny]

    @token_by_email_docs()
    def post(self, request):
        serializer = TokenByEmailSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)

