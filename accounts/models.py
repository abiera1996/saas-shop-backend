from django.utils.timezone import now
from django.db import models
from utils.caching import CacheQueryManager, BaseModelMixin
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin) 
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _ 
from utils import helpers
from accounts.model_manager import UserManager
from django.contrib.auth.hashers import (
    acheck_password,
    check_password,
    is_password_usable,
    make_password,
)


optional = {
    'null': True,
    'blank': True
}
    

class Role(models.Model): 
    name =  models.CharField(max_length=100, **optional) 
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"
    

class PermissionModule(models.Model):   
    PERMISSION_TYPE = (
        (1, 'Backoffice'),
        (2, 'Merchants')
    )

    name = models.CharField(max_length=200)
    order = models.IntegerField(default=0)
    type = models.IntegerField(choices=PERMISSION_TYPE, default=1)

    def __str__(self):
        return self.name 


class Permission(models.Model):    
    name = models.CharField(max_length=200)
    description = models.TextField(**optional)
    code =  models.CharField(max_length=100, unique=True)
    permission_module = models.ForeignKey(PermissionModule, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.code} - {self.name}"
    

class RolePermissionMapping(models.Model):
    
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin, BaseModelMixin):

    AUTH_PROVIDERS = (
        (1, 'facebook'),
        (2, 'google'),
        (3, 'email')
    )

    first_name = models.CharField(max_length=255, **optional )
    last_name = models.CharField(max_length=255, **optional )
    username = models.CharField(max_length=255, unique=True, db_index=True) 
    avatar = models.ImageField(upload_to=helpers.upload_avatar_to, help_text="Form data as file type.", **optional)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    last_login = models.DateTimeField(_('last login'), blank=True, null=True)
    auth_provider = models.IntegerField(choices=AUTH_PROVIDERS, default=1)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, **optional)

    USERNAME_FIELD = 'username'

    objects = UserManager()

    def __str__(self):
        return self.username

    def tokens(self):  
        from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
        
        # Blacklist all outstanding tokens for this user
        tokens = OutstandingToken.objects.filter(user=self)
        for token in tokens:
            BlacklistedToken.objects.get_or_create(token=token)

        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }


class Contact(models.Model):
    CONTACT_TYPE = (
        (1, 'Mobile'),
        (2, 'Email')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contact_type = models.IntegerField(choices=CONTACT_TYPE, default=1)
    is_primary = models.BooleanField(default=False)
    contact_value = models.CharField(max_length=255, **optional ) 


class Region(models.Model):
    region = models.CharField(max_length=255, **optional )

    def __str__(self):
        return self.region 

class Province(models.Model):
    province = models.CharField(max_length=255, **optional )
    region = models.ForeignKey(Region, on_delete=models.CASCADE)

    def __str__(self):
        return self.province 


class City(models.Model):
    city = models.CharField(max_length=255, **optional )
    province = models.ForeignKey(Province, on_delete=models.CASCADE)

    def __str__(self):
        return self.city 

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255 )
    address2 = models.CharField(max_length=255, **optional )
    city = models.ForeignKey(City, on_delete=models.CASCADE)
