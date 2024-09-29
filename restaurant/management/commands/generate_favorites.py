from django.core.management.base import BaseCommand
from restaurant.models import Restaurant, Favorite
from accounts.models import CustomUser  # Adjust the path to your CustomUser model
import random

class Command(BaseCommand):
    help = 'Generate mock favorite records for the Favorite model'

    def handle(self, *args, **kwargs):
        customers = CustomUser.objects.filter(account_type=1)  # Select customers with account_type = 1
        restaurants = Restaurant.objects.all()

        if not customers.exists():
            self.stdout.write(self.style.ERROR('No customers found with account_type=1.'))
            return

        if not restaurants.exists():
            self.stdout.write(self.style.ERROR('No restaurants found.'))
            return

        # Select one-third of the customers
        customer_subset = random.sample(list(customers), len(customers) // 3)

        created_count = 0

        for customer in customer_subset:
            # Randomly determine the number of favorite restaurants for this customer (1 to 8)
            favorite_count = random.randint(1, 8)
            
            # Randomly select restaurants to be favorites
            favorite_restaurants = random.sample(list(restaurants), favorite_count)

            for restaurant in favorite_restaurants:
                # Create a favorite entry for each selected restaurant
                Favorite.objects.create(
                    customer=customer,
                    restaurant=restaurant
                )
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Total {created_count} favorite records created successfully!'))
