from django.urls import path
from . import views

from django.urls import path
from . import views

urlpatterns = [
    path('', views.ActiveBookingsView.as_view(), name='booking-list'),
    path('<int:pk>/', views.BookingDetailView.as_view(), name='booking-detail'),
    path('start-rental/', views.start_rental, name='start-rental'),
    path('<int:pk>/end-rental/', views.end_rental, name='end-rental'),
    path('completed/', views.CompletedBookingsView.as_view(), name='completed-bookings'),
]