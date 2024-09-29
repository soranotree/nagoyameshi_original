from django.core.management.base import BaseCommand
from django.utils.timezone import now
from accounts.models import CustomUser
from random import randint
import random
import numpy as np
from faker import Faker
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    # python manage.py help <カスタムコマンド名> を実行すると表示されるメッセージ
    help = "Help message"

    def add_arguments(self, parser):
        # オプションをつけたい場合のみ必要
        pass

    def handle(self, *args, **kwargs):
        fake = Faker('ja_JP')

        for _ in range(50):
            account_type = random.choice([1, 2])  # Randomly select an account type
            is_subscribed = random.choice([True, False])  # Randomly decide if the user is subscribed or not
            card_number = fake.credit_card_number() if is_subscribed else None

            # Create a new CustomUser instance with random data
            user = CustomUser.objects.create(
                user_name=fake.name(),
                username=fake.user_name(),
                email=fake.email(),
                password=make_password(fake.password()),
                account_type=account_type,
                is_subscribed=is_subscribed,
                card_number=card_number,
                card_name=fake.name() if is_subscribed else None,
                expiry=fake.credit_card_expire() if is_subscribed else None,
                last_login=now(),  # Ensure correct timezone.now() usage
                is_superuser=False,
                is_staff=False,
                is_active=True,
                date_joined=fake.date_this_decade(before_today=True, after_today=False),
                created_at=now(),  # Use now() for timestamp fields
                updated_at=now()
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created user {user.username}'))