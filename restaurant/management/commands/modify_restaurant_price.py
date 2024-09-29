from django.core.management.base import BaseCommand
from restaurant.models import Restaurant, Menu

class Command(BaseCommand):
    help = 'Update the price range for each restaurant based on its menus, with commas for thousands.'

    def handle(self, *args, **kwargs):
        restaurants = Restaurant.objects.all()

        for restaurant in restaurants:
            # Query the Menu model for the restaurant to find min and max prices
            menus = Menu.objects.filter(restaurant=restaurant)
            
            if menus.exists():
                min_price = menus.order_by('price').first().price
                max_price = menus.order_by('-price').first().price

                # Format the price with commas for thousands
                formatted_min_price = f"{min_price:,}"
                formatted_max_price = f"{max_price:,}"

                # Update the price field as "min_price円～max_price円"
                restaurant.price = f"{formatted_min_price}円～{formatted_max_price}円"

                # Save the updated restaurant object
                restaurant.save()
                self.stdout.write(self.style.SUCCESS(f"Updated {restaurant.shop_name} with price range {restaurant.price}."))
            else:
                self.stdout.write(self.style.WARNING(f"No menus found for {restaurant.shop_name}, skipping."))
