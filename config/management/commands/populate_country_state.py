from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
import os
import json  
from accounts.models import Country, State, City
from django.db import transaction


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 

    migration_folder = os.path.join(BASE_DIR, '../../migration_files/countries+states+cities.json')

    def chunked_delete(self, qs, size=500):
        while qs.exists():
            ids = list(qs.values_list("id", flat=True)[:size])
            qs.filter(id__in=ids).delete()

    def handle(self, *args, **options):
        import time

        start = time.time()
        print("Starting") 

        with open(self.migration_folder, encoding='utf-8-sig') as f:
            data = json.load(f)
        rows = data 
 
        with transaction.atomic():
            for details in rows:
                timezone = ''
                if details['timezones']:
                    timezone = details['timezones'][0]['zoneName']
                country = Country.objects.create(
                    country_code=details['iso2'],
                    country=details['name'],
                    timezone=timezone
                )
                
                for state in details['states']: 
                    state_obj = State.objects.create(
                        country=country,
                        state=state['name'],
                        state_code=state['iso2']
                    ) 
                    cities_to_create = list()
                    for city in state['cities']: 
                        cities_to_create.append(
                            City(
                                state=state_obj,
                                city=city["name"]
                            )
                        ) 
                    City.objects.bulk_create(cities_to_create)
        end = time.time()
        self.stdout.write(self.style.SUCCESS('%f seconds' % (end - start)))
        self.stdout.write(self.style.SUCCESS('Successfully populate'))
 