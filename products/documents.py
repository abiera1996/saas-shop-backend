from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from .models import Product

@registry.register_document
class ProductDocument(Document):
    # Map the related shop to allow filtering by slug
    shop = fields.ObjectField(properties={
        'slug': fields.KeywordField(),
    })
    
    category = fields.ObjectField(properties={
        'name': fields.KeywordField(),
        'slug': fields.KeywordField(),
    })
    
    brand = fields.ObjectField(properties={
        'name': fields.KeywordField(),
        'slug': fields.KeywordField(),
    })

    rating = fields.FloatField()

    def prepare_rating(self, instance):
        return instance.average_rating

    class Index:
        # Name of the Elasticsearch index
        name = 'products'
        # See Elasticsearch Indices API reference for available settings
        settings = {'number_of_shards': 1, 'number_of_replicas': 0}

    class Django:
        model = Product # The model associated with this Document

        # The fields of the model you want to be indexed in Elasticsearch
        fields = [
            'name',
            'description',
            'price',
            'inventory_count',
        ]
        
        # We need to add related_models to update ES when Shop changes, 
        # but for products we usually only care when the Product itself changes.
