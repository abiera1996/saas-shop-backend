from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path, include 
from rest_framework import routers
from .views import AuthenticationView, LocationView

authentication_routers  = routers.DefaultRouter(trailing_slash=False)
authentication_routers.register('', AuthenticationView, basename='authentication')

location_routers = routers.DefaultRouter(trailing_slash=False)
location_routers.register('', LocationView, basename='location')

urlpatterns = [ 
    path('authentication/', include(authentication_routers.urls)), 
    path('location/', include(location_routers.urls)),
] 

 