# Generated by Django 4.2 on 2024-10-01 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0021_restaurant_max_price_restaurant_min_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='reservation_num',
            field=models.IntegerField(default=0, verbose_name='予約数'),
        ),
        migrations.AddField(
            model_name='restaurant',
            name='review_num',
            field=models.IntegerField(default=0, verbose_name='レビュー数'),
        ),
    ]
