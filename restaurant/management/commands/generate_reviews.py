from django.core.management.base import BaseCommand
from restaurant.models import Restaurant, Review
from accounts.models import CustomUser
from faker import Faker
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Generate 1,000 mock reviews for the Review model'

    def handle(self, *args, **kwargs):
        fake = Faker('ja_JP')  # Set locale to Japanese
        customers = CustomUser.objects.filter(account_type=1)  # Select customers with account_type = 1
        restaurants = Restaurant.objects.all()

        if not customers.exists():
            self.stdout.write(self.style.ERROR('No customers found with account_type=1.'))
            return

        if not restaurants.exists():
            self.stdout.write(self.style.ERROR('No restaurants found.'))
            return

        review_count = 1000
        created_count = 0

        for _ in range(review_count):
            customer = random.choice(customers)
            restaurant = random.choice(restaurants)
            
            # Generate a past date for visit_date
            visit_date = fake.date_between(start_date='-6y', end_date='today')
            
            # Randomly generate a comment in Japanese
            comment = fake.text(max_nb_chars=200)
            
            # Randomly generate a rate between 1 and 5
            rate = random.randint(1, 5)
            
            # Randomly select reply (either "null" or a fake Japanese reply)
            reply = random.choice([None, fake.sentence()])

            # Create a new review
            Review.objects.create(
                customer=customer,
                restaurant=restaurant,
                visit_date=visit_date,
                comment=comment,
                rate=rate,
                display_masked=0,  # Set display masked to 0 (not masked)
                reply=reply
            )
            
            created_count += 1
            if created_count % 100 == 0:
                self.stdout.write(self.style.SUCCESS(f'{created_count} reviews created...'))

        self.stdout.write(self.style.SUCCESS(f'Total {created_count} mock reviews created successfully!'))
