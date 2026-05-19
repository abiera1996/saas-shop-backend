from utils import serializers as class_serializer
from rest_framework import serializers 
from accounts.models import User, Contact
from django.contrib.auth import authenticate
from django.utils.timezone import now
from utils import helpers
from utils.social import google, register
from config import settings
from rest_framework.exceptions import AuthenticationFailed


class UserDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'avatar', 'date_joined', 'last_login', 'role')


class LoginSerializer(class_serializer.ModelSerializer):
    """
    LoginSerializer
    """

    username = serializers.CharField(max_length=255, min_length=3)
    password = serializers.CharField(max_length=68, min_length=3) 
    
    class Meta:
        model = User
        fields = ('username', 'password')
    
    def validate(self, attrs):
        errors = dict()
        request = self.context.get('request') 
        contact = Contact.objects.filter(contact_value=attrs['username'], is_primary=True)
        username = ''
        if contact.exists(): 
            username = contact[0].contact_value 
         
        user = authenticate(request, username=username, password=attrs['password']) 
        if user is None:
            errors['generic'] = 'Username or password is invalid.' 
            
        # Check if it has errors
        if errors:
            raise serializers.ValidationError(errors)
        attrs['user'] = user
        return attrs

    def save(self, **kwargs): 
        request = self.context.get('request')
        data = dict(self.validated_data.items()) 
        user = data['user']
        user.last_login = now() 
        user.save()
        return {
            **UserDetailsSerializer(user).data, 
            'token': user.tokens()
        }
 

class GoogleSocialAuthSerializer(class_serializer.Serializer):
    auth_token = serializers.CharField() 
    is_register = serializers.BooleanField(default=False)

    def validate(self, attrs):
        errors = dict() 
        request = self.context.get('request')
        user_data = google.Google.validate(attrs['auth_token'])
        try:
            user_data['sub']
        except:
            errors['generic'] = 'The token is invalid or expired. Please login again.' 
        if not errors:
            if user_data['aud'] != settings.GOOGLE_CLIENT_ID:
                errors['generic'] = 'oops, who are you?' 

            user_id = user_data['sub']
            email = user_data['email']
            name = user_data.get('name', '')
            first_name = user_data.get('given_name', '')
            last_name = user_data.get('family_name', '')
            provider = 'google'
            try:
                return register.register_social_user(
                    request=request,
                    provider=provider, 
                    user_id=user_id, 
                    email=email, 
                    first_name=first_name, 
                    last_name=last_name, 
                    is_register=attrs.get('is_register', False)
                )
            except Exception as identifier: 
                errors['generic'] = str(identifier)
    
        raise serializers.ValidationError(errors)
    
    def save(self, **kwargs):
        data = dict(self.validated_data.items()) 
        return data