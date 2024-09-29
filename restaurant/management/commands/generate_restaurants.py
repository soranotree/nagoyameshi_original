from django.core.management.base import BaseCommand
from faker import Faker
from accounts.models import CustomUser
from restaurant.models import Restaurant, Category
from django.utils.timezone import now

fake = Faker('ja_JP') 

class Command(BaseCommand):
    help = 'Generate random restaurants'

    def handle(self, *args, **kwargs):
        shop_owners = CustomUser.objects.filter(account_type=2) 
        categories = Category.objects.all()

        if not shop_owners.exists():
            self.stdout.write(self.style.ERROR('No shop owners found. Please create some shop owners first.'))
            return

        if not categories.exists():
            self.stdout.write(self.style.ERROR('No categories found. Please create some categories first.'))
            return

        for _ in range(100): 
            shop_owner = fake.random_element(shop_owners)  # Random shop owner
            category = fake.random_element(categories)  # Random category

            restaurant = Restaurant.objects.create(
              shop_owner=shop_owner,
              category=category,
            #   rateはreviewで持たせている。restaurantでは不要
            #   rate=round(fake.random.uniform(1.0, 5.0), 1),  # Random rate between 1.0 and 5.0
              zip_code=fake.zipcode(),
              shop_name=fake.company(),
              address=fake.address(),
              phone=fake.phone_number(),
              owner_name=fake.name(),  
              email=fake.email(),  # Use shop owner's email
              description = fake.sentence(nb_words=10),  # Generate a Japanese sentence with approximately 10 words
              business_time = f"{fake.time(pattern='%H:%M')}～{fake.time(pattern='%H:%M')}",  # Random business hours in hh:mm～hh:mm format
            #   business_time=f"{fake.time()} - {fake.time()}",  # Random business hours
              close_day_of_week = fake.random_element(['月', '火', '水', '木', '金', '土', '日']),
              created_at=now(),
              updated_at=now()
              )
            
            self.stdout.write(self.style.SUCCESS(f'Successfully created restaurant {restaurant.shop_name}'))
