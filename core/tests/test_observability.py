import pytest
import uuid
from rest_framework.test import APIClient
from django.urls import reverse
from core.exceptions.codes import ErrorCode

@pytest.fixture
def client():
    return APIClient()

from django.urls import path
from rest_framework.views import APIView
from rest_framework.exceptions import APIException
from django.test import override_settings

class ErrorView(APIView):
    def get(self, request):
        raise APIException("Test error")

urlpatterns = [
    path('test-error/', ErrorView.as_view()),
]

@pytest.mark.urls(__name__)
@pytest.mark.django_db
class TestObservability:
    def test_request_id_generated_missing_header(self, client):
        """
        Test that a request ID is generated if the header is missing.
        """
        # Even on 404, middleware runs.
        response = client.get('/random-404-url/')
        assert 'X-Request-ID' in response.headers
        assert len(response.headers['X-Request-ID']) > 0

    def test_request_id_preserved_existing_header(self, client):
        """
        Test that the provided request ID is preserved.
        """
        custom_id = str(uuid.uuid4())
        response = client.get('/random-404-url/', HTTP_X_REQUEST_ID=custom_id)
        
        assert response.headers['X-Request-ID'] == custom_id

    def test_request_id_in_error_response(self, client):
        """
        Test that the request ID is included in the error payload.
        """
        # Hit the error view
        response = client.get('/test-error/')
        
        # It should process valid DRF exception and return 500 (or whatever APIException defaults to, usually 500)
        # Actually APIException without status_code is 500.
        # But wait, default APIException status_code is 500.
        # Let's check the handler logical again. 
        # "if isinstance(exc, APIException): ... else: code = ErrorCode.SERVER_ERROR"
        
        assert response.status_code == 500
        data = response.json()
        
        assert not data['success']
        assert 'request_id' in data
        assert len(data['request_id']) > 0
        assert data['request_id'] == response.headers['X-Request-ID']

    def test_long_request_id_truncated_or_regenerated(self, client):
        """
        Middleware logic says: if > 100 chars, regenerate.
        """
        long_id = "a" * 101
        response = client.get('/random-404-url/', HTTP_X_REQUEST_ID=long_id)
        
        assert response.headers['X-Request-ID'] != long_id
        assert len(response.headers['X-Request-ID']) > 0
