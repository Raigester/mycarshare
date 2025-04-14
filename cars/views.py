from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import CarBrand, CarModel, Car, CarPhoto, CarReview
from .serializers import (
    CarBrandSerializer, CarModelSerializer, CarSerializer, 
    CarDetailSerializer, CarPhotoSerializer, CarReviewSerializer
)

class CarBrandViewSet(viewsets.ModelViewSet):
    """API for car brands"""
    
    queryset = CarBrand.objects.all()
    serializer_class = CarBrandSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class CarModelViewSet(viewsets.ModelViewSet):
    """API for car models"""
    
    queryset = CarModel.objects.all()
    serializer_class = CarModelSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = ['brand']

class CarViewSet(viewsets.ModelViewSet):
    """API for cars"""
    
    queryset = Car.objects.all()
    serializer_class = CarSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['model__name', 'model__brand__name', 'color', 'license_plate']
    filterset_fields = {
        'model': ['exact'],
        'fuel_type': ['exact'],
        'transmission': ['exact'],
        'seats': ['exact', 'gte', 'lte'],
        'year': ['exact', 'gte', 'lte'],
        'price_per_hour': ['gte', 'lte'],
        'price_per_day': ['gte', 'lte'],
        'status': ['exact'],
        'has_air_conditioning': ['exact'],
        'has_gps': ['exact'],
        'has_child_seat': ['exact'],
    }
    ordering_fields = ['price_per_hour', 'price_per_day', 'rating', 'year', 'mileage']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CarDetailSerializer
        return CarSerializer
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def change_status(self, request, pk=None):
        """Change car status (admin only)"""
        car = self.get_object()
        status = request.data.get('status')
        
        if status not in [choice[0] for choice in Car.STATUS_CHOICES]:
            return Response({"status": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
        
        car.status = status
        car.save()
        
        return Response({"message": f"Status changed to {status}"})
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def update_location(self, request, pk=None):
        """Update car location (admin only)"""
        car = self.get_object()
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')
        
        if not latitude or not longitude:
            return Response({"error": "Coordinates are missing"}, status=status.HTTP_400_BAD_REQUEST)
        
        car.current_latitude = latitude
        car.current_longitude = longitude
        car.save()
        
        return Response({"message": "Location updated"})

class CarPhotoViewSet(viewsets.ModelViewSet):
    """API for car photos"""
    
    queryset = CarPhoto.objects.all()
    serializer_class = CarPhotoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['car']
    
    def get_queryset(self):
        # Add the ability to get photos by car ID
        car_id = self.request.query_params.get('car_id')
        if car_id:
            return CarPhoto.objects.filter(car_id=car_id)
        return super().get_queryset()

class CarReviewViewSet(viewsets.ModelViewSet):
    """API for car reviews"""
    
    queryset = CarReview.objects.all()
    serializer_class = CarReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['car', 'user', 'rating']
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
        # Recalculate the car's average rating
        car = serializer.validated_data['car']
        reviews = CarReview.objects.filter(car=car)
        avg_rating = reviews.aggregate(models.Avg('rating'))['rating__avg']
        car.rating = avg_rating
        car.save()
