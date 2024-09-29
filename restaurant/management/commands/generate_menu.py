from django.core.management.base import BaseCommand
from faker import Faker
from restaurant.models import Restaurant, Menu
from datetime import datetime

fake = Faker('ja_JP')

class Command(BaseCommand):
    help = 'Generate random menus for restaurants'

    def handle(self, *args, **kwargs):
        restaurants = Restaurant.objects.all()

        if not restaurants.exists():
            self.stdout.write(self.style.ERROR('No restaurants found.'))
            return

        for restaurant in restaurants:
            if not Menu.objects.filter(restaurant=restaurant).exists():
                business_times = restaurant.business_time.split("～")
                business_start = business_times[0]
                business_end = business_times[1]

                # Create 6 menus for the restaurant
                # 1st Menu
                Menu.objects.create(
                    restaurant=restaurant,
                    name=fake.word() + " 特選セット",
                    description=f"{restaurant.shop_name}の創業の精神が宿る、渾身の一品",
                    price=fake.random_element([600, 700, 800, 850, 900, 950, 1000, 1100, 1200]),
                    available_from=datetime.strptime(business_start, "%H:%M").time(),
                    available_end=datetime.strptime(business_end, "%H:%M").time(),
                )

                # 2nd Menu
                Menu.objects.create(
                    restaurant=restaurant,
                    name=fake.word() + " 自信の一品",
                    description=f"{restaurant.shop_name}自信の一品です",
                    price=fake.random_element([600, 700, 800, 850, 900, 950, 1000, 1100, 1200]),
                    available_from=datetime.strptime(business_start, "%H:%M").time(),
                    available_end=datetime.strptime(business_end, "%H:%M").time(),
                )

                # 3rd Menu (lunch time)
                Menu.objects.create(
                    restaurant=restaurant,
                    name=fake.word() + " 日替わりランチ",
                    description=f"このお値段でこれだけの満足",
                    price=fake.random_element([800, 850, 900, 950, 1000, 1100, 1200]),
                    available_from=datetime.strptime("11:30", "%H:%M").time(),
                    available_end=datetime.strptime("14:00", "%H:%M").time(),
                )

                # 4th Menu (lunch time)
                Menu.objects.create(
                    restaurant=restaurant,
                    name=fake.word() + " ランチセット",
                    description=f"きょうのランチは{fake.word()}で決まり！",
                    price=fake.random_element([800, 850, 900, 950, 1000, 1100, 1200]),
                    available_from=datetime.strptime("11:30", "%H:%M").time(),
                    available_end=datetime.strptime("14:00", "%H:%M").time(),
                )

                # 5th Menu (dinner)
                Menu.objects.create(
                    restaurant=restaurant,
                    name=fake.word() + " 豪華ディナーコース",
                    description=f"大切な接待にぴったりのコースメニュー",
                    price=fake.random_element([5000, 7000, 8000, 10000, 12000, 13000]),
                    available_from=datetime.strptime("17:30", "%H:%M").time(),
                    available_end=datetime.strptime(business_end, "%H:%M").time(),
                )

                # 6th Menu (dinner)
                Menu.objects.create(
                    restaurant=restaurant,
                    name=fake.word() + " フルコース料理",
                    description=f"本場で15年間修業したシェフお勧めの豪華フルコース",
                    price=fake.random_element([10000, 12000, 13000, 14000, 15000, 20000]),
                    available_from=datetime.strptime("18:00", "%H:%M").time(),
                    available_end=datetime.strptime(business_end, "%H:%M").time(),
                )

                self.stdout.write(self.style.SUCCESS(f'Successfully created menus for {restaurant.shop_name}'))

        self.stdout.write(self.style.SUCCESS('Menu generation completed!'))
