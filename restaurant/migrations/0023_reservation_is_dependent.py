# Generated by Django 4.2 on 2024-10-01 11:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0022_restaurant_reservation_num_restaurant_review_num'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='is_dependent',
            field=models.BooleanField(default='0', verbose_name='枠依存用予約フラグ'),
        ),
    ]
