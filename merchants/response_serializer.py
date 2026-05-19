from rest_framework import serializers 


class CustomerRegistrationSuccessResponseSerializer(serializers.Serializer):
    message = serializers.CharField(default="Successfully Register. You can now login your account.",)
    data = serializers.JSONField(
        default=  {
                "success": True
            } 
    )
    code = serializers.CharField(default=None, allow_null=True)


class ErrorFieldCustomerRegistartionSerializer(serializers.Serializer):
    message = serializers.CharField(default="")
    data = serializers.JSONField(
        default=  {
        "error_fields": [
            "email",
            "avatar"
        ],
        "complete_error": {
            "email": [
                "user with this email already exists."
            ],
            "avatar": [
                "The submitted data was not a file. Check the encoding type on the form."
            ]
        }
    }
    )
    status_code = serializers.IntegerField(default=200)