from rest_framework import serializers
from .models import CarBrand, CarModel, Car, CarPhoto, CarReview

class CarBrandSerializer(serializers.ModelSerializer):
    """Serializer for car brands"""
    
    class Meta:
        model = CarBrand
        fields = '__all__'

class CarModelSerializer(serializers.ModelSerializer):
    """Serializer for car models"""
    
    brand_name = serializers.ReadOnlyField(source='brand.name')
    
    class Meta:
        model = CarModel
        fields = ('id', 'brand', 'brand_name', 'name')

class CarPhotoSerializer(serializers.ModelSerializer):
    """Serializer for car photos"""
    
    class Meta:
        model = CarPhoto
        fields = ('id', 'photo', 'caption')

class CarReviewSerializer(serializers.ModelSerializer):
    """Serializer for car reviews"""
    
    user_username = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = CarReview
        fields = ('id', 'user', 'user_username', 'rating', 'comment', 'created_at')
        read_only_fields = ('user', 'created_at')

class CarSerializer(serializers.ModelSerializer):
    """Serializer for cars"""
    
    brand_name = serializers.ReadOnlyField(source='model.brand.name')
    model_name = serializers.ReadOnlyField(source='model.name')
    photos = CarPhotoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Car
        fields = ('id', 'model', 'brand_name', 'model_name', 'year', 'license_plate',
                  'color', 'mileage', 'fuel_type', 'transmission', 'price_per_hour',
                  'price_per_day', 'deposit_amount', 'engine_capacity', 'power', 'seats',
                  'has_air_conditioning', 'has_gps', 'has_child_seat', 'has_bluetooth',
                  'has_usb', 'status', 'current_latitude', 'current_longitude', 
                  'main_photo', 'photos', 'rating')

class CarDetailSerializer(CarSerializer):
    """Extended serializer for car details"""
    
    reviews = CarReviewSerializer(many=True, read_only=True)
    
    class Meta(CarSerializer.Meta):
        fields = CarSerializer.Meta.fields + ('reviews', 'insurance_valid_until', 
                                            'technical_inspection_valid_until', 'created_at', 'updated_at')
