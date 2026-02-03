import uuid
import logging
import time
from django.utils.deprecation import MiddlewareMixin
from core.logging import set_request_id, clear_request_id

logger = logging.getLogger(__name__)

class RequestIDMiddleware(MiddlewareMixin):
    """
    Middleware that:
    1. Generates or extracts a Request ID (UUID).
    2. Sets it in thread locals for logging.
    3. Appends X-Request-ID to the response.
    4. Logs the start and end of the request with execution time.
    """
    
    HEADER_NAME = 'X-Request-ID'

    def process_request(self, request):
        request_id = request.headers.get(self.HEADER_NAME)
        
        # Validate or generate UUID
        if not request_id or len(request_id) > 100:
            request_id = str(uuid.uuid4())
        
        # Attach to request and thread local
        request.id = request_id
        set_request_id(request_id)
        
        request.start_time = time.time()
        
        # Log request start (safe info only)
        # Avoid logging full path or params if they might contain sensitive info, 
        # but method and path are usually safe.
        logger.info(f"Request started: {request.method} {request.path}")

    def process_response(self, request, response):
        if hasattr(request, 'id'):
            response[self.HEADER_NAME] = request.id
            
            # Calculate duration
            if hasattr(request, 'start_time'):
                duration = time.time() - request.start_time
                logger.info(f"Request finished: {request.method} {request.path} - {response.status_code} ({duration:.4f}s)")
            
            clear_request_id()
            
        return response

    def process_exception(self, request, exception):
        # Ensure we clear context even on exception if process_response isn't called
        # (Though process_response usually IS called for handled exceptions, 
        # unhandled ones might bubble up. MiddlewareMixin handles this well usually)
        # We don't clear here immediately because we might want the ID in exception handler.
        # The clean up safely happens in process_response or thread death.
        pass
