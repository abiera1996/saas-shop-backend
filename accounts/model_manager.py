from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin) 
from utils.caching import CacheQueryManager, BaseModelMixin


class UserManager(BaseUserManager, CacheQueryManager):

    def create_user(self, username, role_id, email=None, mobile=None, mobile_country_code='', first_name='', last_name='', auth_provider=3, password=None):
        from accounts.models import Contact
        if username is None:
            raise TypeError('Users should have a username')
 
        user = self.model(
            username=username,  
            first_name=first_name, 
            last_name=last_name,
            auth_provider=auth_provider,
            role_id=role_id
        )
        user.set_password(password) 
        user.save() 
 
        if email:
            Contact.objects.create(
                user=user,
                contact_type=2,
                is_primary=True,
                contact_value=self.normalize_email(email)
            )

        if mobile:
            Contact.objects.create(
                user=user,
                contact_type=1,
                is_primary=True,
                contact_value=mobile,
                country_code=mobile_country_code
            )
        return user

    def create_superuser(self, username, password=None):
        if password is None:
            raise TypeError('Password should not be none') 
        user = self.create_user(
            username=username, 
            role_id=1, 
            email=username, 
            auth_provider=3, 
            password=password
        )
        user.is_superuser = True
        user.is_staff = True
        user.save() 
        return user
    