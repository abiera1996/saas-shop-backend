from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path, include 
from rest_framework import routers
from .views import MerchantView


merchant_routers  = routers.DefaultRouter(trailing_slash=False)
merchant_routers.register('', MerchantView, basename='merchant')

urlpatterns = [ 
    path('merchant/', include(merchant_routers.urls)), 
] 

 