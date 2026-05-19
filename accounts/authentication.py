from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Returns the user model instance associated with the token, if one exists.
        This also checks if the token was issued before the user's last login,
        and if so, denies access, forcing a single active session.
        """
        user = super().get_user(validated_token)
        
        if user and user.last_login:
            # validated_token['iat'] is an integer timestamp
            # user.last_login.timestamp() is a float timestamp
            # If the token was issued before the last login, it's invalid.
            if validated_token.get('iat', 0) < int(user.last_login.timestamp()):
                raise AuthenticationFailed(
                    'This token is no longer valid. User logged in from another device or session.' , 
                    code='new_session'
                )
                
        return user
