from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Booking, BookingHistory
from cars.models import Car

class BookingCreateForm(forms.ModelForm):
    """Форма для створення нового бронювання"""
    
    class Meta:
        model = Booking
        fields = ['car', 'start_time', 'end_time', 'additional_driver', 'baby_seat']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'additional_driver': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'baby_seat': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Тільки доступні автомобілі можна бронювати
        self.fields['car'].queryset = Car.objects.filter(status='available')
        self.fields['car'].widget.attrs.update({'class': 'form-select'})
        
        # Встановлення мінімальних дат для полів часу
        min_date = timezone.now()
        min_date_str = min_date.strftime('%Y-%m-%dT%H:%M')
        
        self.fields['start_time'].widget.attrs.update({'min': min_date_str})
        self.fields['end_time'].widget.attrs.update({'min': min_date_str})
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        car = cleaned_data.get('car')
        
        if start_time and end_time and car:
            # Перевірка, що початковий час раніше кінцевого
            if start_time >= end_time:
                raise ValidationError("Час початку має бути раніше часу завершення")
            
            # Перевірка, що початковий час у майбутньому
            if start_time <= timezone.now():
                raise ValidationError("Час початку має бути у майбутньому")
            
            # Перевірка перетину з іншими бронюваннями
            overlapping_bookings = Booking.objects.filter(
                car=car,
                status__in=['pending', 'confirmed', 'active'],
                start_time__lt=end_time,
                end_time__gt=start_time
            )
            
            if overlapping_bookings.exists():
                raise ValidationError("Автомобіль вже заброньовано на цей період")
            
            # Розрахунок вартості бронювання
            duration = end_time - start_time
            hours = duration.total_seconds() / 3600
            
            # Розрахунок базової вартості (ціна за годину * кількість годин)
            price = car.price_hourly * hours
            
            # Додавання вартості додаткових опцій
            if cleaned_data.get('additional_driver'):
                price += car.price_additional_driver
            
            if cleaned_data.get('baby_seat'):
                price += car.price_baby_seat
            
            self.calculated_price = round(price, 2)
        
        return cleaned_data

class BookingUpdateForm(forms.ModelForm):
    """Форма для оновлення існуючого бронювання"""
    
    class Meta:
        model = Booking
        fields = ['start_time', 'end_time', 'additional_driver', 'baby_seat']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'additional_driver': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'baby_seat': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = kwargs.get('instance')
        
        if instance:
            # Встановити мінімальні значення для дат
            min_date = max(timezone.now(), instance.start_time)
            min_date_str = min_date.strftime('%Y-%m-%dT%H:%M')
            
            self.fields['start_time'].widget.attrs.update({'min': min_date_str})
            self.fields['end_time'].widget.attrs.update({'min': min_date_str})
            
            # Заповнити значення за замовчуванням
            self.fields['start_time'].initial = instance.start_time
            self.fields['end_time'].initial = instance.end_time
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time:
            # Перевірка, що початковий час раніше кінцевого
            if start_time >= end_time:
                raise ValidationError("Час початку має бути раніше часу завершення")
            
            # Перевірка, що якщо бронювання ще не почалося, то початковий час має бути у майбутньому
            instance = self.instance
            if instance.status in ['pending', 'confirmed'] and start_time <= timezone.now():
                raise ValidationError("Для бронювання, яке ще не почалося, час початку має бути у майбутньому")
            
            # Перевірка перетину з іншими бронюваннями
            overlapping_bookings = Booking.objects.exclude(id=instance.id).filter(
                car=instance.car,
                status__in=['pending', 'confirmed', 'active'],
                start_time__lt=end_time,
                end_time__gt=start_time
            )
            
            if overlapping_bookings.exists():
                raise ValidationError("Автомобіль вже заброньовано на цей період")
            
            # Розрахунок вартості бронювання
            duration = end_time - start_time
            hours = duration.total_seconds() / 3600
            
            # Розрахунок базової вартості (ціна за годину * кількість годин)
            price = instance.car.price_hourly * hours
            
            # Додавання вартості додаткових опцій
            if cleaned_data.get('additional_driver'):
                price += instance.car.price_additional_driver
            
            if cleaned_data.get('baby_seat'):
                price += instance.car.price_baby_seat
            
            self.calculated_price = round(price, 2)
        
        return cleaned_data

class BookingCancelForm(forms.Form):
    """Форма для скасування бронювання"""
    confirm_cancel = forms.BooleanField(
        required=True,
        label="Я підтверджую скасування бронювання",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

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
            # Перевірка балансу користувача
            try:
                balance = self.user.balance
                min_required = car.price_per_minute * 60  # Мінімум на 1 годину
                
                if balance.amount < min_required:
                    raise ValidationError(f"Недостатньо коштів на балансі. Мінімальний необхідний баланс: {min_required} ₴")
            except:
                raise ValidationError("У користувача відсутній баланс")
        
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

class AdminBookingStatusForm(forms.Form):
    """Форма для адміністратора для зміни статусу бронювання"""
    status = forms.ChoiceField(
        choices=Booking.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label="Примітки"
    )

class BookingFilterForm(forms.Form):
    """Форма для фільтрації бронювань"""
    STATUS_CHOICES = (
        ('', 'Усі статуси'),
        ) + tuple(Booking.STATUS_CHOICES)

    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    car = forms.ModelChoiceField(
        queryset=Car.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Усі автомобілі"
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )