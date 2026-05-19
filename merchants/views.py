from rest_framework import viewsets, status
from . import serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.decorators import api_view, permission_classes as view_permission
from django.db.models.functions import Concat, Lower
from django.db.models import CharField, Value as V, Q
from datetime import datetime, timedelta, date
from accounts.models import (User)
from merchants.models import Merchant
from django.http import HttpResponse  
from dateutil.relativedelta import relativedelta
import string
from django.db import transaction
import requests
from django.db.models.functions import Coalesce
from django.db.models import F, Count, IntegerField, Subquery, OuterRef, Case, When
from django.template.loader import get_template, render_to_string
from drf_spectacular.utils import (OpenApiResponse, extend_schema, OpenApiExample)
from . import response_serializer
from django.contrib.auth import password_validation
from utils import global_response_serializer
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from utils.permissions import SecretKeySitesPermission


@extend_schema( 
    tags=['Merchant']
)
class MerchantView(viewsets.GenericViewSet):
    http_method_names = ['post','get']
    permission_classes = (AllowAny,)
    queryset = Merchant.objects.all()
    serializer_class = serializers.MerchantDetailsSerializer
    action_serializers = {
        'register': serializers.MerchantRegistrationSerializer
    }

    def get_serializer_class(self):
        """
        Retrieve the appropriate serializer for every request method
        """
        if hasattr(self, 'action_serializers'):
            if self.action in self.action_serializers:
                return self.action_serializers[self.action]

        return super(MerchantView, self).get_serializer_class()
    
    @extend_schema(  
        summary='Merchant Details',
        responses={
            200: global_response_serializer.SuccessResponseLoginSerializer,
            401: global_response_serializer.NewSessionErrorSerializer
        }
    )
    @action(detail=False, methods=['get'], url_path='me', permission_classes=[IsAuthenticated])
    def me(self, request, *args, **kwargs):
        """
        Get the merchant details of the authenticated merchant.
        """ 
        merchant = None
        if not hasattr(request.user, 'merchant'):
            return Response({
                "message": "This account is not authorized as a merchant.",
                "data": {},
                "code": 0
            }, status=status.HTTP_401_UNAUTHORIZED)
        merchant = request.user.merchant
        serializer = self.get_serializer(merchant) 
        return Response(serializer.data, status=status.HTTP_200_OK) 

    @extend_schema(  
        auth=[],
        parameters=list([
            OpenApiParameter(
                name="api-key", location=OpenApiParameter.HEADER, type=OpenApiTypes.STR, required=False, default="")
        ]),
        summary='Merchant Registration',
        responses={
            200: response_serializer.CustomerRegistrationSuccessResponseSerializer,
            400: response_serializer.ErrorFieldCustomerRegistartionSerializer,
            401: global_response_serializer.AuthenticationErrorSerializer
        }
    )
    @action(detail=False, methods=['post'], url_path='register', permission_classes=[SecretKeySitesPermission])
    def register(self, request, *args, **kwargs):
        """
        Merchant registration setup.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(instance, 
                        status=status.HTTP_200_OK if instance['success'] else status.HTTP_400_BAD_REQUEST )
        return Response(serializer.get_error_response(), status=status.HTTP_400_BAD_REQUEST)