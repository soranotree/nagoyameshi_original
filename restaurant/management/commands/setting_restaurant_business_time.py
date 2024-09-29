from django.core.management.base import BaseCommand
from restaurant.models import Restaurant
import random

class Command(BaseCommand):
    help = 'Update the business_time for all restaurants'

    def handle(self, *args, **kwargs):
        # Possible start and end times
        start_times = ["09:00", "09:30", "10:00", "10:30", "11:00"]
        end_times = ["21:00", "21:30", "22:00", "22:30"]

        # Get all restaurants
        restaurants = Restaurant.objects.all()

        if not restaurants.exists():
            self.stdout.write(self.style.ERROR('No restaurants found.'))
            return

        for restaurant in restaurants:
            # Randomly pick a start and end time
            start_time = random.choice(start_times)
            end_time = random.choice(end_times)

            # Update the business_time
            restaurant.business_time = f"{start_time}～{end_time}"
            restaurant.save()

            self.stdout.write(self.style.SUCCESS(f'Updated {restaurant.shop_name} to {start_time}～{end_time}'))

        self.stdout.write(self.style.SUCCESS('Business time update completed!'))
