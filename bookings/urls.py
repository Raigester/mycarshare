from django.urls import path
from . import views

urlpatterns = [
    # Список активних бронювань
    path('', views.ActiveBookingsView.as_view(), name='booking-list'),
    
    # Деталі конкретного бронювання
    path('<int:pk>/', views.BookingDetailView.as_view(), name='booking-detail'),
    
    # Початок оренди
    path('start-rental/', views.start_rental, name='start-rental'),
    
    # Завершення оренди
    path('<int:pk>/end-rental/', views.end_rental, name='end-rental'),
    
    # Список завершених бронювань
    path('completed/', views.CompletedBookingsView.as_view(), name='completed-bookings'),
]