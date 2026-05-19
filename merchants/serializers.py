from utils import helpers, serializers as class_serializer
from rest_framework import serializers 
from accounts.models import (User, Contact)
from merchants.models import Merchant
from django.db.models import CharField, Value as V, Q, Sum
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from django.db import transaction
from accounts.serializers import UserDetailsSerializer


class MerchantDetailsSerializer(class_serializer.ModelSerializer):
    user = UserDetailsSerializer()

    class Meta:
        model = Merchant
        fields = '__all__'
    

class MerchantRegistrationSerializer(class_serializer.ModelSerializer):
    """
    MerchantRegistrationSerializer
    """   
    business_name = serializers.CharField() 
    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = ('email', 'password', 'business_name')
    
    def validate(self, attrs):
        errors = dict()
        request = self.context.get('request')  
        try:
            password_validation.validate_password(attrs['password'])
        except ValidationError as e: 
            errors['password'] = e.messages

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
            user = User.objects.create_user(
                username=data['email'], 
                password=data['password'],
                role_id=3, # Merchant Role,
                email=data['email'],
            )
            
            Merchant.objects.create(
                user=user,
                business_name=data['business_name']
            )
        return {
            'success': True,
            'message': "Successfully Register. You can now login your account."
        }

