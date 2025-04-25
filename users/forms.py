from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from .models import User, DriverLicenseVerification

class UserRegistrationForm(UserCreationForm):
    """Form for user registration"""
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(required=False, max_length=17)
    date_of_birth = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 
                 'last_name', 'phone_number', 'date_of_birth')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email already in use")
        return email

class UserProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile"""
    date_of_birth = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'date_of_birth', 'profile_picture')
        widgets = {
            'profile_picture': forms.FileInput(),
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    """Form for changing user password"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})

class DriverLicenseVerificationForm(forms.ModelForm):
    """Form for driver license verification"""
    
    class Meta:
        model = DriverLicenseVerification
        fields = ('front_image', 'back_image', 'selfie_with_license')
        widgets = {
            'front_image': forms.FileInput(attrs={'class': 'form-control'}),
            'back_image': forms.FileInput(attrs={'class': 'form-control'}),
            'selfie_with_license': forms.FileInput(attrs={'class': 'form-control'}),
        }

class AdminVerificationForm(forms.ModelForm):
    """Form for admins to approve/reject license verification"""
    
    class Meta:
        model = DriverLicenseVerification
        fields = ('status', 'comment')
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class BalanceAddForm(forms.Form):
    """Form for adding funds to user balance"""
    amount = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        min_value=0.01,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )