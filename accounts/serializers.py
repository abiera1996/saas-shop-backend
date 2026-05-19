from rest_framework import serializers
from .models import Merchant

class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = ('id', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        merchant = Merchant.objects.create_user(
            email=validated_data['email'],
            username=validated_data['email'], # default username to email
            password=validated_data['password']
        )
        return merchant
