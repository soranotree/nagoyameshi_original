from django.core.management.base import BaseCommand
from faker import Faker

class Command(BaseCommand):
    # python manage.py help <カスタムコマンド名> を実行すると表示されるメッセージ
    help = "Help message"

    def add_arguments(self, parser):
        # オプションをつけたい場合のみ必要
        pass

    def handle(self, *args, **options):
        # 具体的な処理内容
        print("Hello, World!")
        
        fake = Faker('jp_JP')
        print(fake.name())
        print(fake.address())