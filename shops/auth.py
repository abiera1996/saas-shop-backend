import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework import authentication
from rest_framework import exceptions
from .models import Customer

class CustomerJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.DecodeError:
            raise exceptions.AuthenticationFailed('Invalid token')

        customer_id = payload.get('customer_id')
        shop_id = payload.get('shop_id')

        if not customer_id or not shop_id:
            raise exceptions.AuthenticationFailed('Invalid token payload')

        try:
            customer = Customer.objects.get(id=customer_id, shop_id=shop_id)
        except Customer.DoesNotExist:
            raise exceptions.AuthenticationFailed('Customer not found')

        return (customer, token)

def generate_customer_token(customer):
    payload = {
        'customer_id': customer.id,
        'shop_id': customer.shop_id,
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
