# Generated by Django 5.2 on 2025-04-27 15:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cars', '0005_remove_car_price_per_day_remove_car_price_per_hour'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='car',
            name='deposit_amount',
        ),
    ]
