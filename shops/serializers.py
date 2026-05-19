from rest_framework import serializers
from .models import Shop

class ShopSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()
    brands = serializers.SerializerMethodField()

    class Meta:
        model = Shop
        fields = ('id', 'name', 'slug', 'description', 'theme_color', 'categories', 'brands')

    def get_categories(self, obj):
        return list(obj.categories.values('id', 'name', 'slug'))

    def get_brands(self, obj):
        return list(obj.brands.values('id', 'name', 'slug'))
