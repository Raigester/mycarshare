from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from .models import Booking
from carsharing.celery import app

@app.task
def process_minute_billing():
    """Process billing for active bookings"""
    now = timezone.now()
    active_bookings = Booking.objects.filter(
        status='active'
    )
    
    for booking in active_bookings:
        with transaction.atomic():
            # Get the user's balance
            try:
                user_balance = booking.user.balance
            except:
                # If the user has no balance, end the booking
                booking.status = 'completed'
                booking.end_time = now
                booking.save()
                
                # Update the car's status
                car = booking.car
                car.status = 'available'
                car.save()
                continue
            
            # Calculate unpaid minutes
            if booking.last_billing_time:
                time_diff = now - booking.last_billing_time
                minutes_to_bill = int(time_diff.total_seconds() / 60)
            else:
                # If this is the first billing, start from the current moment
                minutes_to_bill = 1
                booking.last_billing_time = now
            
            if minutes_to_bill > 0:
                # Cost for unpaid minutes
                amount_to_bill = booking.car.price_per_minute * Decimal(str(minutes_to_bill))
                
                # Check if there are enough funds
                if user_balance.amount >= amount_to_bill:
                    # Deduct the money
                    user_balance.amount -= amount_to_bill
                    user_balance.save()
                    
                    # Update the last billing time and the number of billed minutes
                    booking.last_billing_time = now
                    booking.minutes_billed += minutes_to_bill
                    booking.save()
                else:
                    # Insufficient funds - end the booking
                    booking.status = 'completed'
                    booking.end_time = now
                    booking.save()
                    
                    # Update the car's status
                    car = booking.car
                    car.status = 'available'
                    car.save()
