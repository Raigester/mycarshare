# Generated by Django 5.2 on 2025-04-20 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0004_remove_payment_booking_remove_payment_description_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='payment_provider',
            field=models.CharField(choices=[('liqpay', 'LiqPay'), ('wayforpay', 'WayForPay')], max_length=20),
        ),
    ]
