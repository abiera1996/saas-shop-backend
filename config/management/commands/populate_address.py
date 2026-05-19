from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
import os
import json 
from dateutil.relativedelta import relativedelta 
from app_user.models import Region, City, Province

class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
    migration_folder = os.path.join(BASE_DIR, 'commands/import_files')

    def handle(self, *args, **options):
        import time 
        
        start = time.time()      

        with open(os.path.join(self.migration_folder, 'philippines.json'), encoding='utf-8-sig') as f:
            data = json.load(f)
        rows = data   

        for index, key in enumerate(rows):   
            region_details = rows[key] 
            region,_ = Region.objects.get_or_create(region=region_details['region_name'])

            for key2 in region_details['province_list']:  
                province_details = region_details['province_list'][key2] 
                province,_ = Province.objects.get_or_create(province=key2, region=region)

                for key3 in province_details['municipality_list']:  
                    City.objects.get_or_create(city=key3, province=province)

        end = time.time()
        self.stdout.write(self.style.SUCCESS('%f seconds' % (end - start)))
        self.stdout.write(self.style.SUCCESS('Successfully setup'))
 