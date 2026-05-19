from django.contrib.auth.models import AbstractUser
from django.db import models

class Merchant(AbstractUser):
    # We will use email as the primary login identifier
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    # username is still required by AbstractUser unless we override it completely, 
    # but we can just require it for createsuperuser.
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
