from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class Booking(models.Model):
    """Model for car bookings"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending confirmation'),
        ('confirmed', 'Confirmed'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]
    
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='bookings')
    car = models.ForeignKey('cars.Car', on_delete=models.CASCADE, related_name='bookings')
    
    # Booking time
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    # Locations
    pickup_location = models.CharField(max_length=255, blank=True)
    return_location = models.CharField(max_length=255, blank=True)
    
    # Status and information
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Additional options
    additional_driver = models.BooleanField(default=False)
    baby_seat = models.BooleanField(default=False)
    
    # System information
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Booking {self.id} - {self.car} ({self.status})"
    
    def clean(self):
        """Model validation"""
        
        # Check that start time is earlier than end time
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be earlier than end time")
        
        # Check that start time is in the future (on creation)
        if not self.id and self.start_time <= timezone.now():
            raise ValidationError("Start time must be in the future")
        
        # Check for overlapping bookings in the same period
        overlapping_bookings = Booking.objects.exclude(id=self.id).filter(
            car=self.car,
            status__in=['pending', 'confirmed', 'active'],
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        )
        
        if overlapping_bookings.exists():
            raise ValidationError("The car is already booked for this period")
    
    def save(self, *args, **kwargs):
        # Perform validation before saving
        self.clean()
        
        # If this is a new booking and the status is confirmed, update the car's status
        if not self.id and self.status in ['confirmed', 'active']:
            self.car.status = 'busy'
            self.car.save()
        
        super().save(*args, **kwargs)

class BookingHistory(models.Model):
    """Model for booking history (to track changes)"""
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='history')
    status = models.CharField(max_length=20, choices=Booking.STATUS_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"History {self.booking.id} - {self.status} ({self.timestamp})"
