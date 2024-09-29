from django.core.management.base import BaseCommand
import random
from restaurant.models import Restaurant
from datetime import time


class Command(BaseCommand):
    help = 'Modify '

    def handle(self, *args, **kwargs):
        # Define the choices
        A_part = ['なら当店へ！', 'の新コンセプト。', 'の老舗。', 'をお探しなら。']
        B_part = ['癒しの時間をご提供いたします。', 'お一人でもお仲間とでも！', 'どんなシーンでもお任せください！']
        C_part = ['スタッフ一同、お待ち申し上げております。', '心のこもったおもてなしをご堪能下さい。', 'ゆっくりとお寛ぎください。']
        # Query to get all records with id > 10
        restaurants = Restaurant.objects.filter(id__gt=10)
        for restaurant in restaurants:
            new_description = f"{restaurant.category.name}{random.choice(A_part)}{random.choice(B_part)}{random.choice(C_part)}"
            # Update name and description
            restaurant.description = new_description
            # Save the changes
            restaurant.save()
        print(f"{restaurants.count()} records updated successfully!")
