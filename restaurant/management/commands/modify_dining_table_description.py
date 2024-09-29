from django.core.management.base import BaseCommand
import random
from restaurant.models import DiningTable
from datetime import time

class Command(BaseCommand):
    help = 'Modify '

    def handle(self, *args, **kwargs):
        # Fetch all DiningTable records where id is greater than 22
        tables = DiningTable.objects.filter(id__gt=22)
        # Loop through the records and replace "様" with "名様"
        for table in tables:
            if "様" in table.name_for_customer:
                table.name_for_customer = table.name_for_customer.replace("様", "名様")
                table.save()  # Save each updated record
                
        print(f"{tables.count()} records updated successfully!")
