from django.urls import path
from . import views

urlpatterns = [
    # Основні представлення для бронювань
    path('', views.BookingListView.as_view(), name='booking-list'),
    path('<int:pk>/', views.BookingDetailView.as_view(), name='booking-detail'),
    path('create/', views.BookingCreateView.as_view(), name='booking-create'),
    path('<int:pk>/update/', views.BookingUpdateView.as_view(), name='booking-update'),
    path('<int:pk>/cancel/', views.cancel_booking, name='booking-cancel'),
    
    # Представлення для активного використання
    path('start-rental/', views.start_rental, name='start-rental'),
    path('<int:pk>/end-rental/', views.end_rental, name='end-rental'),
    
    # Представлення для фільтрації бронювань
    path('active/', views.ActiveBookingsView.as_view(), name='active-bookings'),
    path('upcoming/', views.UpcomingBookingsView.as_view(), name='upcoming-bookings'),
    
    # Адміністративні представлення
    path('<int:pk>/change-status/', views.AdminBookingChangeStatusView.as_view(), name='admin-change-status'),
]