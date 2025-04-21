from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CarBrandViewSet, CarModelViewSet, CarViewSet, 
    CarPhotoViewSet, CarReviewViewSet
)

router = DefaultRouter()
router.register(r'cars', CarViewSet)
router.register(r'brands', CarBrandViewSet)
router.register(r'models', CarModelViewSet)
router.register(r'photos', CarPhotoViewSet)
router.register(r'reviews', CarReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
