from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from ..docs import signup_docs
from ..serializers import SignupSerializer, SignupResponseSerializer


class SignupView(APIView):
    permission_classes = [AllowAny]

    @signup_docs()
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        return Response(SignupResponseSerializer(user).data, status=status.HTTP_201_CREATED)
