from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PaymentViewSet, PaymentTransactionViewSet, PaymentSuccessView,
    PaymentCancelView, WayForPayCallbackView, LiqPayCallbackView
)

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'transactions', PaymentTransactionViewSet, basename='transaction')

urlpatterns = [
    path('', include(router.urls)),
    path('success/', PaymentSuccessView.as_view(), name='payment-success'),
    path('cancel/', PaymentCancelView.as_view(), name='payment-cancel'),
    path('webhook/wayforpay/', WayForPayCallbackView.as_view(), name='wayforpay-callback'),
    path('webhook/liqpay/', LiqPayCallbackView.as_view(), name='liqpay-callback'),
]
