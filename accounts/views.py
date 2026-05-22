from rest_framework import viewsets, status
from . import serializers
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.decorators import api_view, permission_classes as view_permission
from django.db.models.functions import Concat, Lower
from django.db.models import CharField, Value as V, Q
from datetime import datetime, timedelta, date
from accounts.models import User, Country, State, City
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


@extend_schema( 
    tags=['Authentication']
)
class AuthenticationView(viewsets.GenericViewSet):
    http_method_names = ['post','get']
    permission_classes = (AllowAny,)
    queryset = User.objects.all()
    serializer_class = serializers.LoginSerializer
    action_serializers = {
        'login': serializers.LoginSerializer,
        'google': serializers.GoogleSocialAuthSerializer
    }

    def get_serializer_class(self):
        """
        Retrieve the appropriate serializer for every request method
        """
        if hasattr(self, 'action_serializers'):
            if self.action in self.action_serializers:
                return self.action_serializers[self.action]

        return super(AuthenticationView, self).get_serializer_class()
    
    @extend_schema( 
        auth=[],
        summary='Credential login',
        responses={
            200: global_response_serializer.SuccessResponseLoginSerializer,
            400: response_serializer.InvalidCredentialLoginSerializer,
        }
    )
    @action(detail=False, methods=['post'], url_path='login', permission_classes=[AllowAny])
    def login(self, request, *args, **kwargs):
        """
        This is to login the user using his/her credentials.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(instance, status=status.HTTP_200_OK)
        return Response(serializer.get_error_response(), status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema( 
        summary='Google login',
        auth=[]
    )
    @action(detail=False, methods=['post'], url_path='google', permission_classes=[AllowAny])
    def google(self, request, *args, **kwargs):
        """
        This is to login the user using his/her google account.
        """

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            instance = serializer.save()
            return Response(instance, status=status.HTTP_200_OK)
        return Response(serializer.get_error_response(), status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema( 
        auth=[],
        summary='Get Password Requirements',
        responses=response_serializer.SuccessResponsePasswordRequirementsSerializer
    )
    @action(detail=False, methods=['get'], url_path='password-requirements', permission_classes=[AllowAny])
    def get_password_requirements(self, request, *args, **kwargs):
        """
        This is list of password format and requirements.
        """ 
        return Response({
            'password_requirements': password_validation.password_validators_help_texts()
        } , status=status.HTTP_200_OK)

class LocationView(viewsets.GenericViewSet):
    permission_classes = (AllowAny,)
    
    @action(detail=False, methods=['get'], url_path='countries')
    def countries(self, request, *args, **kwargs):
        queryset = Country.objects.all().order_by('country')
        
        queryset = Country.objects.all() 
        if data.get('search'):
            search =  data.get('search')
            orm_lookups = ['country__icontains']
            
            queryset = helpers.search_result(queryset, search, orm_lookups, 0, False)
        queryset = helpers.Paginator(queryset).paginate(page=data.get('page',1), limit=data.get('limit', 10))
        
        serializer = serializers.CountrySerializer(queryset.get('data', None), many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='states')
    def states(self, request, *args, **kwargs):
        country_id = request.query_params.get('country_id')
        if not country_id:
            return Response({'success': False, 'message': 'country_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        queryset = State.objects.filter(country_id=country_id).order_by('state')
        serializer = serializers.StateSerializer(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='cities')
    def cities(self, request, *args, **kwargs):
        state_id = request.query_params.get('state_id')
        if not state_id:
            return Response({'success': False, 'message': 'state_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        queryset = City.objects.filter(state_id=state_id).order_by('city')
        serializer = serializers.CitySerializer(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
