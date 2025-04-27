from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from carsharing.celery import app

from .models import Booking


@app.task
def process_minute_billing():
    """Обробка білінгу для активних бронювань"""
    now = timezone.now()
    active_bookings = Booking.objects.filter(
        status="active"
    )

    for booking in active_bookings:
        with transaction.atomic():
            # Отримати баланс користувача
            try:
                user_balance = booking.user.balance
            except:
                # Якщо у користувача немає балансу, завершити бронювання
                booking.status = "completed"
                booking.end_time = now
                booking.save()

                # Оновити статус автомобіля
                car = booking.car
                car.status = "available"
                car.save()
                continue

            # Розрахувати неоплачені хвилини
            if booking.last_billing_time:
                time_diff = now - booking.last_billing_time
                minutes_to_bill = int(time_diff.total_seconds() / 60)
            else:
                # Якщо це перший білінг, почати з поточного моменту
                minutes_to_bill = 1
                booking.last_billing_time = now

            if minutes_to_bill > 0:
                # Вартість неоплачених хвилин
                amount_to_bill = booking.car.price_per_minute * Decimal(str(minutes_to_bill))

                # Перевірити, чи достатньо коштів
                if user_balance.amount >= amount_to_bill:
                    # Списати гроші
                    user_balance.amount -= amount_to_bill
                    user_balance.save()

                    # Оновити час останнього білінгу та кількість оплачуваних хвилин
                    booking.last_billing_time = now
                    booking.minutes_billed += minutes_to_bill
                    booking.save()
                else:
                    # Недостатньо коштів - завершити бронювання
                    booking.status = "completed"
                    booking.end_time = now
                    booking.save()

                    # Оновити статус автомобіля
                    car = booking.car
                    car.status = "available"
                    car.save()
