from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)
    # Now add the HTTP status code to the response.
    if response is not None: 
        if 'data' in response.data: 
            if response.data['data'] == 'None':
                response.data.pop('data')
        if 'code' in response.data:
            if str(response.data['code']) == 'token_not_valid':
                response.data.pop('detail')
                message = response.data.pop('messages') 
                response.data = {
                    'message': message[0]['message'],
                    'code': response.data.pop('code')
                }
        if 'detail' in response.data:
            message = response.data.pop('detail') 
            response.data['message'] = message
    return response 