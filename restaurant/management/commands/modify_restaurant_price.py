from django.core.management.base import BaseCommand
from restaurant.models import Restaurant, Menu

class Command(BaseCommand):
    help = 'Update the price range for each restaurant based on its menus, with commas for thousands.'

    def handle(self, *args, **kwargs):
        restaurants = Restaurant.objects.all()

        for restaurant in restaurants:
            # Query the Menu model for the restaurant and aggregate min/max price
            menus = Menu.objects.filter(restaurant=restaurant)
            
            if menus.exists():
                prices = menus.values_list('price', flat=True)
                min_price = min(prices)
                max_price = max(prices)

                # Update the restaurant with the new price range
                restaurant.min_price = min_price
                restaurant.max_price = max_price

                # Save the updated restaurant object
                restaurant.save()

                self.stdout.write(self.style.SUCCESS(
                    f"Updated {restaurant.shop_name} with price range {min_price:,}円 to {max_price:,}円."
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f"No menus found for {restaurant.shop_name}, skipping."
                ))
