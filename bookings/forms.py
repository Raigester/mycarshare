from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Booking, BookingHistory
from cars.models import Car

class BookingStartRentalForm(forms.Form):
    """Форма для початку оренди автомобіля"""
    car = forms.ModelChoiceField(
        queryset=Car.objects.filter(status='available'),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    latitude = forms.FloatField(
        required=False,
        widget=forms.HiddenInput()
    )
    
    longitude = forms.FloatField(
        required=False,
        widget=forms.HiddenInput()
    )
    
    confirm_start = forms.BooleanField(
        required=True,
        label="Я підтверджую, що ознайомився з умовами оренди та починаю поїздку",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        car = cleaned_data.get('car')
        
        if car and self.user:
            balance = getattr(self.user, 'balance', None)
            
            min_required = car.price_per_minute * 60
            
            if balance.amount < min_required:
                raise ValidationError(f"Недостатньо коштів на балансі. Мінімальний необхідний баланс: {min_required} ₴")
        
        return cleaned_data

class BookingEndRentalForm(forms.Form):
    """Форма для завершення оренди автомобіля"""
    latitude = forms.FloatField(
        required=False,
        widget=forms.HiddenInput()
    )
    
    longitude = forms.FloatField(
        required=False,
        widget=forms.HiddenInput()
    )
    
    confirm_end = forms.BooleanField(
        required=True,
        label="Я підтверджую завершення оренди",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )