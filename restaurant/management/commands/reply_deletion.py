from django.core.management.base import BaseCommand
import random
from restaurant.models import Review

class Command(BaseCommand):
    help = 'Generate mock favorite records for the Favorite model'

    def handle(self, *args, **kwargs):
      # Fetch all reviews
      reviews = Review.objects.all()
      # Calculate XX% of the total number of reviews
      num_to_nullify = int(len(reviews) * 0.15)
      # Randomly select 30% of the reviews
      reviews_to_nullify = random.sample(list(reviews), num_to_nullify)
      # Nullify the 'reply' field for the selected reviews
      for review in reviews_to_nullify:
        review.reply = None
        review.save()  # Save the changes to the database
        
      print(f"Nullified the reply field for {num_to_nullify} reviews.")
