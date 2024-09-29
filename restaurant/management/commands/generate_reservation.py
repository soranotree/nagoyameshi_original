from django.core.management.base import BaseCommand
from restaurant.models import Restaurant, DiningTable, Reservation
from datetime import datetime, timedelta, time
import random

class Command(BaseCommand):
    help = 'Create mock reservations for each restaurant and dining table'

    def handle(self, *args, **kwargs):
        # Get the start date (tomorrow) and end date (XX days from today)
        start_date = datetime.today() + timedelta(days=1)
        end_date = start_date + timedelta(days=3)

        # Get all restaurants and dining tables
        restaurants = Restaurant.objects.all()
        if not restaurants.exists():
            self.stdout.write(self.style.ERROR('No restaurants found.'))
            return

        for restaurant in restaurants:
            business_time = restaurant.business_time
            start_str, end_str = business_time.split("～")
            start_time = datetime.strptime(start_str, "%H:%M").time()
            end_time = datetime.strptime(end_str, "%H:%M").time()

            # Get all dining tables for the restaurant
            dining_tables = DiningTable.objects.filter(restaurant=restaurant)
            if not dining_tables.exists():
                self.stdout.write(self.style.ERROR(f'No dining tables found for restaurant {restaurant.shop_name}.'))
                continue
              
            for dining_table in dining_tables:
              for single_date in (start_date + timedelta(days=n) for n in range((end_date - start_date).days)):
                # Create reservations with time slots every 30 minutes
                current_time = datetime.combine(single_date, start_time)
                end_time_dt = datetime.combine(single_date, end_time)
                
                # while current_time <= (end_time - timedelta(hours=2)):
                while current_time <= (end_time_dt - timedelta(hours=2)):
                  # Determine duration based on the time of day
                  if current_time.time() <= time(17, 0):
                    duration = 60  # 60 minutes for slots before or at 17:00
                  else:
                    duration = 120  # 120 minutes for slots after 17:00
                    
                  # Create the reservation
                  Reservation.objects.create(
                    restaurant=restaurant,
                    dining_table=dining_table,
                    date=single_date.date(),
                    time_start=current_time.time(),
                    duration_min=duration,
                    number_of_people=None,
                    is_booked=False,
                    customer=None,
                    menu=None,
                    )
                  # Increment the time by 30 minutes
                  current_time += timedelta(minutes=30)

        self.stdout.write(self.style.SUCCESS('Mock reservations created successfully!'))
