from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, InvoiceViewSet

router = DefaultRouter()
router.register(r'invoices', InvoiceViewSet)
router.register(r'', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
