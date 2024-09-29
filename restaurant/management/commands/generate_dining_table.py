from django.core.management.base import BaseCommand
from faker import Faker
from restaurant.models import Restaurant
from restaurant.models import DiningTable

fake = Faker('ja_JP')

class Command(BaseCommand):
    help = 'Generate random dining tables for each restaurant'

    def handle(self, *args, **kwargs):
        restaurants = Restaurant.objects.all()
        # restaurants = Restaurant.objects.filter(id__in=[224, 225])
        
        if not restaurants.exists():
            self.stdout.write(self.style.ERROR('No restaurants found. Please create some restaurants first.'))
            return

        for restaurant in restaurants:
            # if not DiningTable.objects.filter(restaurant=restaurant).exists():
                for i in range(1, 11):  # Add 5 dining tables per restaurant
                    max_people = fake.random_element([2, 4, 6, 10, 12])
                    if max_people == 2:
                        min_people = fake.random_element([1, 2])
                    elif max_people == 4:
                        min_people = fake.random_element([2, 3, 4])
                    elif max_people == 6:
                        min_people = fake.random_element([3, 4])
                    elif max_people == 10:
                        min_people = 6
                    else:
                        min_people = 7  # For 12 max_people

                    # Generate random names for internal and customer use
                    name_for_internal = f"No. {i} テーブル"
                    name_for_customer = fake.random_element([
                        f"{max_people}名様 ゆったり席",
                        f"{max_people}名様用 窓側席",
                        f"{max_people}名様用 個室席"
                    ])

                    # Create the dining table
                    dining_table = DiningTable.objects.create(
                        restaurant=restaurant,
                        name_for_internal=name_for_internal,
                        name_for_customer=name_for_customer,
                        min_people=min_people,
                        max_people=max_people,
                    )

                    self.stdout.write(self.style.SUCCESS(f'Successfully created dining table {dining_table.name_for_internal} for restaurant {restaurant.shop_name}'))

        self.stdout.write(self.style.SUCCESS('Dining table generation completed!'))
