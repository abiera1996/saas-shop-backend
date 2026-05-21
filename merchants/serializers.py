from utils import helpers, serializers as class_serializer
from rest_framework import serializers 
from accounts.models import (User, Contact, ActivationCode, City)
from merchants.models import Merchant
from django.db.models import CharField, Value as V, Q, Sum
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.db import transaction
from accounts.serializers import UserDetailsSerializer
from accounts import utils
from audit.models import AuditLog
from django.utils import timezone
import string
import json

class MerchantDetailsSerializer(class_serializer.ModelSerializer):
    user = UserDetailsSerializer()

    class Meta:
        model = Merchant
        fields = '__all__'
    

class MerchantInitialRegistrationSerializer(class_serializer.ModelSerializer):
    """
    MerchantRegistrationSerializer
    """   
    business_name = serializers.CharField() 
    email = serializers.EmailField() 
    phone_number = serializers.CharField() 
    phone_country_code= serializers.CharField() 
    
    class Meta:
        model = User
        fields = ('email', 'business_name', 'phone_number', 'phone_country_code')
    
    def validate(self, attrs):
        errors = dict()
        request = self.context.get('request')  
        # try:
        #     password_validation.validate_password(attrs['password'])
        # except ValidationError as e: 
        #     errors['password'] = e.messages

        contact = Contact.objects.filter(
            is_primary=True,
            contact_type=2,
            contact_value=attrs['email']
        )

        if contact.exists(): 
            errors['email'] = "Email " + attrs['email'] + " already exists."

        # Check if it has errors
        if errors:
            raise serializers.ValidationError(errors) 
        return attrs

    def save(self, **kwargs): 
        request = self.context.get('request')
        data = dict(self.validated_data.items())   

        with transaction.atomic():  
            audit = AuditLog.objects.create(
                audit_type = 1,
                status = 0,
                event = 0,
                search = data['business_name'] + '~' + data['email'],
                new_details = json.dumps(data)  
            )
            
            otp_data = {
                "request_type":  ActivationCode.REQUEST_TYPE[1][0],
                "contact_value": data['email'],
                "contact_type": ActivationCode.CONTACT_TYPE[1][0],
                "expiration": None,
                "audit": audit.id
            }
            
            response = utils.generate_otp(otp_data, 50, string.ascii_lowercase + string.digits)
            response = {
                **response, 
                **otp_data
            }
            if response['success']: 
                response['message'] = "Activation link sent. Please check your email."
            return response
   

class MerchantRegistrationSerializer(class_serializer.ModelSerializer):
    """
    MerchantRegistrationSerializer
    """   
    activation_code = serializers.CharField() 
    password = serializers.CharField() 
    city = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), required=True,  help_text="City ID")
    
    class Meta:
        model = User
        fields = ('activation_code', 'password', 'city')
    
    def validate(self, attrs):
        errors = dict()
        request = self.context.get('request')  
        try:
            password_validation.validate_password(attrs['password'])
        except ValidationError as e: 
            errors['password'] = e.messages

        activation = ActivationCode.objects.filter(
            code=attrs['activation_code'],
            request_type=1
        )
        if activation.exists():
            activation = activation[0]
            if activation.is_used:
                errors['generic'] = "Activation link already used."
            else:
                date_today = timezone.localtime()
                if activation.expiration < date_today:
                    errors['generic'] = "Activation link already expired."
        else:
            errors['generic'] = "Invalid activation link."

        if not errors:
            contact = Contact.objects.filter(
                is_primary=True,
                contact_type=2,
                contact_value=activation.contact_value
            )

            if contact.exists(): 
                # Reject the auditlog if activation code is not used and not expired
                
                errors['email'] = "Email " + attrs['email'] + " already exists."
                audit = activation.audit
                audit.status = -1
                audit.remarks = "Email " + attrs['email'] + " already exists."
                audit.save()

            else:
                attrs['activation'] = activation

        # Check if it has errors
        if errors:
            if activation:
                activation.is_used = 1
                activation.save()

            raise serializers.ValidationError(errors) 
        return attrs

    def save(self, **kwargs): 
        request = self.context.get('request')
        data = dict(self.validated_data.items()) 
          
        activation = data['activation']
        audit = activation.audit

        with transaction.atomic():  
            audit.status = 1
            audit.save()
            
            activation.is_used = 1
            activation.save()

            audit_data = json.loads(audit.new_details)
            user = User.objects.create_user(
                username=audit_data['email'], 
                password=data['password'],
                role_id=3, # Merchant Role,
                email=audit_data['email'],
                mobile=audit_data['phone_number'],
                mobile_country_code=audit_data['phone_country_code']
            ) 
            
            Merchant.objects.create(
                user=user,
                business_name=audit_data['business_name']
            )
 
            return {
                'success': True,
                'message': 'Merchant successfully registered', 
            }
   