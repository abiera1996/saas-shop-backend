from django.utils.deprecation import MiddlewareMixin
from django.http import QueryDict
from threading import Thread
import logging, socket, time, json, requests
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from rest_framework.renderers import JSONRenderer
from rest_framework import exceptions
from io import BytesIO
from decimal import Decimal


logging = logging.getLogger('django')
exclude_log = ['/docs/schema/', '/docs/schema/swagger-ui/', '/docs/schema/redoc/', '/d-admin/',
               '/d-admin', '/', '/favicon.ico'] 


class LoggingMiddleware(MiddlewareMixin):
    """Request/Response Logging Middleware."""

    def __init__(self, get_response):
        super().__init__(get_response)
        self.get_response = get_response

    def process_request(self, request):
        """Set Request Start Time to measure time taken to service request.""" 
        request.start_time = time.time()
        # dynamically call request attribute and copy 
        # so we can have a mutable dictionary  
        if not request.path in exclude_log and '/d-admin/' not in request.path:
            if request.body: 
                try:
                    request.req_body = json.loads(request.body.decode('utf-8'))
                except:
                    datas = request.body.decode('utf-8').split('&')
                    req_body = dict()
                    for data in datas:
                        details = data.split('=')
                        if len(details)>0:
                            req_body[details[0]] = details[1]
                    request.req_body = req_body

    def process_response(self, request, response):
        """Log data using logger."""
        response['X-Forwarded-Host'] = request.get_host() 
        Thread(
            target=self.extract_log_info, 
            daemon=True, 
            kwargs=({'request':request, 'response':response})
        ).start()
        return response

    def process_exception(self, request, exception):
        """Log Exceptions."""
        trace = []
        tb = exception.__traceback__
        
        while tb is not None:
            trace.append({
                "filename": tb.tb_frame.f_code.co_filename,
                "function_name": tb.tb_frame.f_code.co_name,
                "lineno": tb.tb_lineno
            })
            tb = tb.tb_next
        Thread(
            target=self.extract_log_info, 
            daemon=True, 
            kwargs=({'request':request, 'exception':exception, 'trace':trace})
        ).start()

    def extract_log_info(self, request, response=None, exception=None, trace=None):
        
        """Extract appropriate log info from requests/responses/exceptions."""
        if not request.path in exclude_log and '/d-admin/' not in request.path:
            
            log_data = {
                'request_method': request.method,
                'request_path': request.get_full_path(),
                'server_hostname': socket.gethostname(),
                'run_time': time.time() - request.start_time,
            }

            # check files in request we do this to ensure that we are not logging
            # bytes file data on logs
            if len(request.FILES):
                files = {}
                for file in request.FILES:
                    files[file] = request.FILES[file].name

                log_data['request_files'] = files

            if hasattr(request, 'req_body'):
                log_data['request_body'] = request.req_body
            else:
                log_data['request_body'] = {}
        
            if response:
                log_data['content_type'] = response['content-type'] 
                if response['content-type'] == 'application/json':
                    response_body = response.content
                    
                    try:
                        log_data['response_body'] = json.loads(
                            str(response_body, 'utf-8'))
                    except:
                        log_data['response_body'] = response_body
            
            
            if exception:
                log_data.update({
                    'exception_trace':  {
                        'type': type(exception).__name__,
                        'message': "Exception Error: " + str(exception),
                        'trace': trace
                    }
                })
                logging.error(log_data)
                
            if response:
                if 'text/plain' not in response._content_type_for_repr:
                    if response.status_code in (200, 201):
                        logging.debug(log_data)
                    else:
                        logging.error(log_data)
        

class ResponseHandler(MiddlewareMixin):

    def process_response(self, request, response):
        # handle decryption here
        if '/api/' in request.path:  
            try:
                if hasattr(response, 'data'):
                    response_data = response.data
                else:
                    response_data = json.loads(response.content.decode('utf-8'))
                
                message = None
                if 'message' in response_data:
                    message = response_data.pop('message')

                code = None
                if 'code' in response_data:
                    code = response_data.pop('code')

                response_data = { 
                    'message': message,
                    'data': response_data,
                    'code': code
                }   
                response.data = response_data
                response.content = json.dumps(response.data)
            except Exception as e:
                pass
        return response 