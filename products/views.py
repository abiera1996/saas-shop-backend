from rest_framework import viewsets, permissions
from .models import Product
from shops.models import Shop
from .serializers import ProductSerializer
from rest_framework.exceptions import ValidationError
from .documents import ProductDocument
from elasticsearch_dsl.query import MultiMatch

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Product.objects.none()
        # Return products only for the logged in merchant's shop
        if self.request.user.is_authenticated:
            return Product.objects.filter(shop__merchant=self.request.user)
        return Product.objects.none()

    def perform_create(self, serializer):
        # Ensure the merchant has a shop
        try:
            shop = self.request.user.shop
        except Shop.DoesNotExist:
            raise ValidationError("You must create a shop before adding products.")
        serializer.save(shop=shop)

class StorefrontProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        slug = self.kwargs.get('shop_slug')
        
        q = self.request.query_params.get('q', None)
        category = self.request.query_params.get('category', None)
        brand = self.request.query_params.get('brand', None)
        min_price = self.request.query_params.get('min_price', None)
        max_price = self.request.query_params.get('max_price', None)
        min_rating = self.request.query_params.get('min_rating', None)
        
        if not slug:
            return Product.objects.none()
            
        try:
            # Use Elasticsearch for all queries
            search = ProductDocument.search().filter("term", shop__slug=slug)
            
            if q:
                search = search.query(
                    "multi_match", 
                    query=q, 
                    fields=['name^3', 'description'],
                    fuzziness='AUTO'
                )
            
            if category:
                search = search.filter("term", category__name=category)
            if brand:
                search = search.filter("term", brand__name=brand)
                
            if min_price or max_price:
                price_range = {}
                if min_price:
                    price_range['gte'] = int(float(min_price) * 100)
                if max_price:
                    price_range['lte'] = int(float(max_price) * 100)
                search = search.filter("range", price=price_range)
                
            if min_rating:
                search = search.filter("range", rating={'gte': float(min_rating)})
                
            return search.to_queryset()
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Elasticsearch offline, falling back to DB search: {e}")
            
            from django.db.models import Q, Avg
            qs = Product.objects.filter(shop__slug=slug)
            
            if q:
                qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
            if category:
                qs = qs.filter(category__name=category)
            if brand:
                qs = qs.filter(brand__name=brand)
            if min_price:
                qs = qs.filter(price__gte=int(float(min_price) * 100))
            if max_price:
                qs = qs.filter(price__lte=int(float(max_price) * 100))
            if min_rating:
                qs = qs.annotate(avg_rating=Avg('reviews__rating')).filter(avg_rating__gte=float(min_rating))
                
            return qs
