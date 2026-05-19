from rest_framework import serializers 


class SuccessResponseLoginSerializer(serializers.Serializer):
    message = serializers.CharField(default="OTP Sent. Please check your mobile phone.",)
    data = serializers.JSONField(
        default=  {
                "success": True
            } 
    )
    code = serializers.CharField(default="OTP-S1")


class AuthenticationErrorSerializer(serializers.Serializer):
    message = serializers.CharField(default="Authentication credentials were not provided.")
    data = serializers.JSONField(
        default=  {}
    )
    code = serializers.IntegerField(default=None)


class NewSessionErrorSerializer(serializers.Serializer):
    message = serializers.CharField(default="This token is no longer valid. User logged in from another device or session.")
    data = serializers.JSONField(
        default=  {}
    )
    code = serializers.CharField(default="new_session")