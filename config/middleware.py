import logging
import time

logger = logging.getLogger(__name__)

class APILoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        
        # Process the request
        response = self.get_response(request)
        
        duration = time.time() - start_time
        
        # Only log API requests to avoid spamming admin/static routes
        if request.path.startswith('/api/'):
            logger.info(
                f"[DJANGO API] Method: {request.method} | Path: {request.path} | Status: {response.status_code} | Duration: {duration:.3f}s"
            )
            
        return response
