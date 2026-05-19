from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
import os
import json 
from dateutil.relativedelta import relativedelta 
from accounts.models import Role

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def handle(self, *args, **options):
        import time 
        
        start = time.time()  
        ROLES = [
            {
                'name': 'Super Admin',
                'id': 1,
            },
            {
                'name': 'Back Office',
                'id': 2,
            }, 
            {
                'name': 'Merchant',
                'id': 3
            }
        ]
        for role in ROLES:
            role_obj, _ = Role.objects.get_or_create(id=role['id'])
            role_obj.name = role['name']
            role_obj.save()
        end = time.time()
        self.stdout.write(self.style.SUCCESS('%f seconds' % (end - start)))
        self.stdout.write(self.style.SUCCESS('Successfully setup'))

