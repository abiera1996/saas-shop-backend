import logging
from django.contrib.auth import authenticate
from accounts.models import User
import os
import random
from rest_framework.exceptions import AuthenticationFailed
from config.settings import SOCIAL_SECRET
from django.utils.timezone import now
from django.db.models import Q 



def generate_username(name):

    username = "".join(name.split(' ')).lower()
    if not User.objects.filter(username=username).exists():
        return username
    else:
        random_username = username + str(random.randint(0, 1000))
        return generate_username(random_username)


def register_social_user(request, provider, user_id, email, first_name, last_name='', is_register=False): 
    from accounts.serializers import UserDetailsSerializer
    if email:
        filtered_user = User.objects.filter(email=email) 
    else:
        filtered_user = User.objects.filter(username=user_id) 
    #Login social user
    login_user = None
    if filtered_user.exists(): 
        # if provider == filtered_user[0].profile.auth_provider:

        # registered_user = authenticate(username=user_id, password=SOCIAL_SECRET)
        
        registered_user = filtered_user.first() 
        if is_register: 
            raise AuthenticationFailed(
                detail='Invalid registration as individual user.')
                
        registered_user.last_login = now()
        registered_user.save() 
        login_user = registered_user 
        # else:
        #     raise AuthenticationFailed(
        #         detail='Your ' + provider + ' email is already used as email login. \nPlease continue your login using ' + filtered_user[0].profile.auth_provider)

    #Register social user
    else:  
        user = {
            'username': user_id, 
            'email': email,
            'password': SOCIAL_SECRET,
            'first_name': first_name,
            'last_name': last_name,
            'auth_provider': provider
        }
        logging.info({"message": "Create user "+ provider, "data":user})
        try:
            user = User.objects.create_user(**user)
          
            new_user = authenticate(username=user_id, password=SOCIAL_SECRET)
            new_user.last_login = now()
            new_user.save()
            login_user = new_user
        except Exception as e:
            raise AuthenticationFailed(
                detail=str(e))
    
    return {
        **UserDetailsSerializer(login_user).data, 
        'token': login_user.tokens()
    }