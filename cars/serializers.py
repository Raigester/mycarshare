from rest_framework import serializers
from .models import CarBrand, CarModel, Car, CarPhoto, CarReview

class CarBrandSerializer(serializers.ModelSerializer):
    """Серіалізатор для брендів автомобілів"""
    
    class Meta:
        model = CarBrand
        fields = '__all__'

class CarModelSerializer(serializers.ModelSerializer):
    """Серіалізатор для моделей автомобілів"""
    
    brand_name = serializers.ReadOnlyField(source='brand.name')
    
    class Meta:
        model = CarModel
        fields = ('id', 'brand', 'brand_name', 'name')

class CarPhotoSerializer(serializers.ModelSerializer):
    """Серіалізатор для фотографій автомобілів"""
    
    class Meta:
        model = CarPhoto
        fields = ('id', 'photo', 'caption')

class CarReviewSerializer(serializers.ModelSerializer):
    """Серіалізатор для відгуків про автомобілі"""
    
    user_username = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = CarReview
        fields = ('id', 'user', 'user_username', 'car', 'rating', 'comment', 'created_at')
        read_only_fields = ('user', 'created_at')

class CarSerializer(serializers.ModelSerializer):
    """Серіалізатор для автомобілів"""
    
    brand_name = serializers.ReadOnlyField(source='model.brand.name')
    model_name = serializers.ReadOnlyField(source='model.name')
    photos = CarPhotoSerializer(many=True, read_only=True)
    
    class Meta:
        model = Car
        fields = ('id', 'model', 'brand_name', 'model_name', 'year', 'license_plate',
                  'color', 'mileage', 'fuel_type', 'transmission', 'engine_capacity', 'power', 'seats',
                  'has_air_conditioning', 'has_gps', 'has_child_seat', 'has_bluetooth',
                  'has_usb', 'status', 'current_latitude', 'current_longitude', 
                  'main_photo', 'photos', 'rating')

class CarDetailSerializer(CarSerializer):
    """Розширений серіалізатор для деталей автомобіля"""
    
    reviews = CarReviewSerializer(many=True, read_only=True)
    
    class Meta(CarSerializer.Meta):
        fields = CarSerializer.Meta.fields + ('reviews', 'insurance_valid_until', 
                                            'technical_inspection_valid_until', 'created_at', 'updated_at')
