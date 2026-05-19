from django.utils.timezone import now
from django.db import models
from utils.caching import CacheQueryManager, BaseModelMixin
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin) 
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _ 
from utils import helpers
from accounts.models import User
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
    
 
class Merchant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=255, **optional)
