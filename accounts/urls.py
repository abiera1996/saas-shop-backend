from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path, include 
from rest_framework import routers
from .views import AuthenticationView

authentication_routers  = routers.DefaultRouter(trailing_slash=False)
authentication_routers.register('', AuthenticationView, basename='authentication')
urlpatterns = [ 
    path('authentication/', include(authentication_routers.urls)), 
] 

 