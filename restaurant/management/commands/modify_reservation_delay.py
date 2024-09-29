from django.core.management.base import BaseCommand
from restaurant.models import Reservation
from django.db.models import F
from datetime import timedelta

class Command(BaseCommand):
    help = 'Delay reservation dates by a specified number of days'

    def handle(self, *args, **kwargs):
        # Prompt the user for the number of days to delay
        days = input("Enter the number of days to delay the reservation dates: ")

        try:
            days = int(days)  # Convert the input to an integer
        except ValueError:
            self.stdout.write(self.style.ERROR("Invalid input. Please enter a valid integer."))
            return

        # Delay the reservation dates by the specified number of days
        updated_reservations = Reservation.objects.update(date=F('date') + timedelta(days=days))

        # Print out a success message
        self.stdout.write(self.style.SUCCESS(f'Successfully delayed reservation dates by {days} days. {updated_reservations} reservations updated.'))
