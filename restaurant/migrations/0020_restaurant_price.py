# Generated by Django 4.2 on 2024-09-29 04:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0019_remove_restaurant_category_restaurant_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='price',
            field=models.CharField(default='800円～1,000円', max_length=32, verbose_name='価格帯'),
            preserve_default=False,
        ),
    ]
