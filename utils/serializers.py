from rest_framework import serializers
import json


# ------------- Sample Apply -------------------------
# class MySerializer(class_serializer.Serializer):
#     username = serializers.CharField(required=True, max_length=125)
#     password = serializers.CharField(max_length=120, required=True) 
#     applicationID = serializers.IntegerField()


class BaseSerializer():
    def get_error_response(self):
        error_response = {
            'message': None,
            'error_fields': [],
            'complete_error': {}
        }
        if not self.is_valid():
            errors = json.loads(json.dumps(self.errors)) 
            if 'generic' in errors:
                generic_error = errors.pop('generic')
                error_response['message'] = generic_error[0]
            error_response['complete_error'] = errors

            for error in errors: 
                error_response['error_fields'].append(error)  
        return error_response


class Serializer(BaseSerializer, serializers.Serializer):
    pass


class ModelSerializer(BaseSerializer, serializers.ModelSerializer):
    pass