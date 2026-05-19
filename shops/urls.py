from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ShopViewSet, StorefrontShopViewSet

router = DefaultRouter()
router.register(r'', ShopViewSet, basename='shop')

urlpatterns = [
    path('', include(router.urls)),
]
