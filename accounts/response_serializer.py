from rest_framework import serializers 


class InvalidCredentialLoginSerializer(serializers.Serializer):
    message = serializers.CharField(default="Username or password is invalid.",)
    data = serializers.JSONField(
        default= {
            "error_fields": [],
            "complete_error": {}
        }
    )
    status_code = serializers.IntegerField(default=200)

class SuccessResponsePasswordRequirementsSerializer(serializers.Serializer):
    message = serializers.CharField(default="")
    data = serializers.JSONField(
        default={
                "password_requirements": [
                "Your password can’t be too similar to your other personal information.",
                "Your password must contain at least 8 characters.",
                "Your password can’t be a commonly used password.",
                "Your password can’t be entirely numeric."
                ]
            }
        
    )
    status_code = serializers.IntegerField(default=200)