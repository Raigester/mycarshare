from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import CarBrand, CarModel, Car, CarPhoto, CarReview

class CarBrandForm(forms.ModelForm):
    """Форма для брендів автомобілів"""
    
    class Meta:
        model = CarBrand
        fields = ['name', 'logo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control'})
        }

class CarModelForm(forms.ModelForm):
    """Форма для моделей автомобілів"""
    
    class Meta:
        model = CarModel
        fields = ['brand', 'name']
        widgets = {
            'brand': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'})
        }

class CarForm(forms.ModelForm):
    """Форма для автомобілів"""
    
    class Meta:
        model = Car
        fields = [
            'model', 'year', 'license_plate', 'color', 'mileage', 
            'fuel_type', 'transmission', 'price_per_minute',
            'engine_capacity', 'power', 'seats', 'has_air_conditioning',
            'has_gps', 'has_child_seat', 'has_bluetooth', 'has_usb',
            'status', 'current_latitude', 'current_longitude', 'main_photo',
            'insurance_valid_until', 'technical_inspection_valid_until'
        ]
        widgets = {
            'model': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': '1900', 'max': '2100'}),
            'license_plate': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'mileage': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'fuel_type': forms.Select(attrs={'class': 'form-select'}),
            'transmission': forms.Select(attrs={'class': 'form-select'}),
            'price_per_minute': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'engine_capacity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0'}),
            'power': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'seats': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '10'}),
            'has_air_conditioning': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_gps': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_child_seat': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_bluetooth': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'has_usb': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'current_latitude': forms.TextInput(attrs={'class': 'form-control'}),
            'current_longitude': forms.TextInput(attrs={'class': 'form-control'}),
            'main_photo': forms.FileInput(attrs={'class': 'form-control'}),
            'insurance_valid_until': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'technical_inspection_valid_until': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class CarPhotoForm(forms.ModelForm):
    """Форма для фотографій автомобілів"""
    
    class Meta:
        model = CarPhoto
        fields = ['car', 'photo', 'caption']
        widgets = {
            'car': forms.Select(attrs={'class': 'form-select'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control'})
        }

class CarReviewForm(forms.ModelForm):
    """Форма для відгуків на автомобілі"""
    
    class Meta:
        model = CarReview
        fields = ['car', 'rating', 'comment']
        widgets = {
            'car': forms.Select(attrs={'class': 'form-select'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '5'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': '3'})
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        car = cleaned_data.get('car')
        
        if car and self.user and not self.instance.pk:
            if CarReview.objects.filter(car=car, user=self.user).exists():
                raise ValidationError(_("Ви вже залишили відгук на цей автомобіль."))
        
        return cleaned_data

class CarLocationForm(forms.Form):
    """Форма для оновлення місцезнаходження автомобіля"""
    
    latitude = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    longitude = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

class CarStatusForm(forms.Form):
    """Форма для зміни статусу автомобіля"""
    
    STATUS_CHOICES = Car.STATUS_CHOICES
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class CarFilterForm(forms.Form):
    """Форма для фільтрації автомобілів"""
    
    brand = forms.ModelChoiceField(
        queryset=CarBrand.objects.all(),
        required=False,
        empty_label="Усі бренди",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    model = forms.ModelChoiceField(
        queryset=CarModel.objects.all(),
        required=False,
        empty_label="Усі моделі",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    FUEL_CHOICES = [('', 'Усі типи палива')] + list(Car.FUEL_CHOICES)
    fuel_type = forms.ChoiceField(
        choices=FUEL_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    TRANSMISSION_CHOICES = [('', 'Усі трансмісії')] + list(Car.TRANSMISSION_CHOICES)
    transmission = forms.ChoiceField(
        choices=TRANSMISSION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    STATUS_CHOICES = [('', 'Усі статуси')] + list(Car.STATUS_CHOICES)
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    min_year = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Мін. рік'})
    )
    
    max_year = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Макс. рік'})
    )
    
    min_seats = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Мін. кількість місць', 'min': '1'})
    )
    
    has_air_conditioning = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    has_gps = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    has_child_seat = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )