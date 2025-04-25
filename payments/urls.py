from django.urls import path
from . import views

urlpatterns = [
    # Payment views
    path('', views.PaymentListView.as_view(), name='payment-list'),
    path('<int:pk>/', views.PaymentDetailView.as_view(), name='payment-detail'),
    path('create/', views.CreatePaymentView.as_view(), name='create-payment'),
    path('process/', views.ProcessPaymentView.as_view(), name='payment-process'),
    path('success/', views.PaymentSuccessView.as_view(), name='payment-success'),
    path('cancel/', views.PaymentCancelView.as_view(), name='payment-cancel'),
    
    # Transaction views
    path('transactions/', views.TransactionListView.as_view(), name='transaction-list'),
    
    # Webhook callback
    path('webhook/liqpay/', views.LiqPayCallbackView.as_view(), name='liqpay-callback'),
]