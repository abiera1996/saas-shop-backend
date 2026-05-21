from utils import serializers as class_serializer
from rest_framework import serializers 
from accounts.models import ActivationCode
from django.contrib.auth import authenticate
from dateutil.relativedelta import relativedelta
from django.utils.timezone import now
from django.utils import timezone
from utils import helpers  
from rest_framework.exceptions import AuthenticationFailed
from django.db.models import Q
import string

def generate_otp(data, size=6, chars=string.digits):
    """
    data = {
        "request_type"
        "contact_value"
        "contact_type"
        "expiration",
        "audit"
    }
    """
    code = ''
    unique = False
    while not unique:
        code = helpers.id_generator(size, chars)
        otp = ActivationCode.objects.filter(
            Q(code=code) &
            Q(is_used=False)
        )
        
        if not otp.exists():
            unique = True

    expiration = data.get('expiration')
    if not expiration:
        expiration = timezone.localtime() +  relativedelta(minutes=5)

    ActivationCode.objects.update_or_create(
        contact_value=data['contact_value'],
        defaults={
            'code': code,
            'is_used': False,
            'expiration': expiration,
            'request_type': data['request_type'],
            "audit_id": data.get('audit', None)
        }
    ) 
    print("CODE:", code)
    if data['contact_type'] == 1: # Mobile
        # Send Mobile function
        pass
    else:
        # Send Email Function
        pass
        
    return {
        'success': True, 
        'message': "Successfully generated"
    }