from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Shop
from .serializers import ShopSerializer

class ShopViewSet(viewsets.ModelViewSet):
    serializer_class = ShopSerializer
    
    def get_queryset(self):
        # Only return the shop for the currently logged in merchant
        if getattr(self, 'swagger_fake_view', False):
            return Shop.objects.none()
        if self.request.user.is_authenticated:
            return Shop.objects.filter(merchant=self.request.user)
        return Shop.objects.none()

    def perform_create(self, serializer):
        serializer.save(merchant=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        shop = get_object_or_404(Shop, merchant=request.user)
        serializer = self.get_serializer(shop)
        return Response(serializer.data)

class StorefrontShopViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
