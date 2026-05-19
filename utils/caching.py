from django.db import models
from django.core.cache import cache 
from django.conf import settings

# ------------- Sample Apply -------------------------
# class SampleModel(BaseModelMixin, models.Model):
#     objects = CacheQueryManager()
#     class Meta:
#        managed = False 

class BaseModelMixin: 
    def save(self, *args, **kwargs):  
        super_class = type(self)
        model_name = super_class.__name__
        super_class.objects._remove_cache(model_name)
        super(BaseModelMixin, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super_class = type(self)
        model_name = super_class.__name__
        super_class.objects._remove_cache(model_name)
        super(BaseModelMixin, self).delete(*args, **kwargs) 


class CachedQuerySet(models.QuerySet):

    def __init__(self, *args, key='', **kwargs):
        self.key = key 
        super().__init__(*args, **kwargs)
        
    
    def cache(self, timeout=settings.CACHE_REQUEST_TIMEOUT_SECONDS):   
        key = f"{self.model.__name__}:filter:"
        where = self.query.__dict__.get('where')
        if where:
            filters = where.children
            key += f"{hash(frozenset(filters))}" 
         
        result = cache.get(key) 
        if result is None: 
            print(f"Need to cache: {self.model.__name__}")
            result = list(self)
            cache.set(key, result, timeout=timeout) 
        else:
            print(f"From cache: {self.model.__name__}") 
        return result


class CacheQueryManager(models.Manager): 

    db_using = 'default'

    def __init__(self, db_using='default') -> None:
        self.db_using = db_using
        super().__init__()

    def _remove_cache(self, model_name):
        all_keys = cache.keys('*') 
        # Print all keys
        for key in all_keys:
            if model_name in key:
                cache.delete(key)

    def get_queryset(self):
        return CachedQuerySet(self.model, using=self._db) 
    
    def filter(self, *args, **kwargs):
        # self.key = f"{self.model.__name__}:filter:{hash(frozenset(kwargs.items()))}"  
        return self.get_queryset().using(self.db_using).filter(*args, **kwargs)
    
    def all(self): 
        return self.get_queryset().using(self.db_using)

    def get(self, *args, **kwargs):
        return self.get_queryset().using(self.db_using).get(*args, **kwargs)
     