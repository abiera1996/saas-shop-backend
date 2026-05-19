from rest_framework import serializers
from .models import Product, Category, Brand
from django.utils.text import slugify

class ProductSerializer(serializers.ModelSerializer):
    average_rating = serializers.FloatField(read_only=True)
    category = serializers.CharField(source='category.name', allow_null=True, required=False)
    brand = serializers.CharField(source='brand.name', allow_null=True, required=False)

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'category', 'brand', 'price', 'inventory_count', 'image_url', 'average_rating')

    def create(self, validated_data):
        category_data = validated_data.pop('category', None)
        brand_data = validated_data.pop('brand', None)
        
        product = Product.objects.create(**validated_data)
        shop = product.shop
        
        if category_data and category_data.get('name'):
            name = category_data['name']
            category, _ = Category.objects.get_or_create(shop=shop, name=name, defaults={'slug': slugify(name)})
            product.category = category
            
        if brand_data and brand_data.get('name'):
            name = brand_data['name']
            brand, _ = Brand.objects.get_or_create(shop=shop, name=name, defaults={'slug': slugify(name)})
            product.brand = brand
            
        if category_data or brand_data:
            product.save()
            
        return product
