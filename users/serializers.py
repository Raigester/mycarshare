from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import DriverLicenseVerification

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Серіалізатор для моделі User"""
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                  'phone_number', 'date_of_birth', 'profile_picture', 
                  'is_verified_driver', 'rating', 'is_blocked', 'created_at')
        read_only_fields = ('is_verified_driver', 'rating', 'is_blocked', 'created_at')

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Серіалізатор для реєстрації користувача"""
    
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 
                  'last_name', 'phone_number', 'date_of_birth')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Паролі не співпадають"})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class DriverLicenseVerificationSerializer(serializers.ModelSerializer):
    """Серіалізатор для верифікації водійського посвідчення"""
    
    class Meta:
        model = DriverLicenseVerification
        fields = ('id', 'user', 'front_image', 'back_image', 'selfie_with_license', 
                  'status', 'comment', 'created_at')
        read_only_fields = ('status', 'comment', 'created_at', 'user')

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Серіалізатор для оновлення профілю користувача"""
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone_number', 'date_of_birth', 'profile_picture')

class ChangePasswordSerializer(serializers.Serializer):
    """Серіалізатор для зміни пароля"""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Паролі не співпадають"})
        return attrs
