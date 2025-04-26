from decimal import Decimal
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView, View
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseForbidden

from users.models import UserBalance
from payments.models import PaymentTransaction
from .models import Booking, BookingHistory
from .forms import (
    BookingCreateForm, BookingUpdateForm, BookingCancelForm, 
    BookingStartRentalForm, BookingEndRentalForm, AdminBookingStatusForm,
    BookingFilterForm
)

class BookingListView(LoginRequiredMixin, ListView):
    """View for listing user's bookings"""
    model = Booking
    template_name = 'bookings/booking_list.html'
    context_object_name = 'bookings'
    paginate_by = 10
    
    def get_queryset(self):
        """Get filtered bookings for the current user or all for admin"""
        user = self.request.user
        
        # Base queryset - user's bookings or all for admin
        if user.is_staff:
            queryset = Booking.objects.all()
        else:
            queryset = Booking.objects.filter(user=user)
        
        # Apply filters if form submitted
        form = BookingFilterForm(self.request.GET)
        if form.is_valid():
            # Filter by status
            if form.cleaned_data.get('status'):
                queryset = queryset.filter(status=form.cleaned_data['status'])
            
            # Filter by car
            if form.cleaned_data.get('car'):
                queryset = queryset.filter(car=form.cleaned_data['car'])
            
            # Filter by date range
            if form.cleaned_data.get('date_from'):
                date_from = form.cleaned_data['date_from']
                queryset = queryset.filter(
                    Q(start_time__date__gte=date_from) | Q(end_time__date__gte=date_from)
                )
                
            if form.cleaned_data.get('date_to'):
                date_to = form.cleaned_data['date_to']
                queryset = queryset.filter(
                    Q(start_time__date__lte=date_to) | Q(end_time__date__lte=date_to)
                )
                
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        """Add booking stats and filter form to context"""
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Add filter form
        context['filter_form'] = BookingFilterForm(self.request.GET)
        
        # Add booking statistics
        if user.is_staff:
            bookings = Booking.objects.all()
        else:
            bookings = Booking.objects.filter(user=user)
        
        context['total_bookings'] = bookings.count()
        context['active_bookings'] = bookings.filter(status='active').count()
        context['upcoming_bookings'] = bookings.filter(
            status__in=['pending', 'confirmed'],
            start_time__gt=timezone.now()
        ).count()
        context['completed_bookings'] = bookings.filter(status='completed').count()
        
        # Get active and upcoming bookings for quick access
        now = timezone.now()
        context['user_active_bookings'] = bookings.filter(
            status='active',
            start_time__lte=now,
            end_time__gte=now
        )
        
        context['user_upcoming_bookings'] = bookings.filter(
            status__in=['pending', 'confirmed'],
            start_time__gt=now
        ).order_by('start_time')[:5]
        
        return context

class BookingDetailView(LoginRequiredMixin, DetailView):
    """View for booking details"""
    model = Booking
    template_name = 'bookings/booking_detail.html'
    context_object_name = 'booking'
    
    def get_queryset(self):
        """Ensure users can only see their own bookings unless they're staff"""
        user = self.request.user
        if user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(user=user)
    
    def get_context_data(self, **kwargs):
        """Add booking history to context"""
        context = super().get_context_data(**kwargs)
        booking = self.get_object()
        
        # Get booking history
        context['history'] = BookingHistory.objects.filter(booking=booking).order_by('-timestamp')
        
        # Check if booking can be cancelled
        context['can_cancel'] = booking.status in ['pending', 'confirmed']
        
        # Check if booking is active
        context['is_active'] = booking.status == 'active'
        
        # Calculate booking duration
        if booking.status == 'active':
            # For active bookings, calculate from start time to now
            now = timezone.now()
            duration = now - booking.start_time
            hours = duration.total_seconds() / 3600
            context['current_duration_hours'] = round(hours, 1)
            
            # Estimated cost so far
            if booking.minutes_billed > 0:
                context['current_cost'] = booking.car.price_per_minute * Decimal(str(booking.minutes_billed))
            else:
                context['current_cost'] = Decimal('0.00')
        
        return context

class BookingCreateView(LoginRequiredMixin, CreateView):
    """View for creating a new booking"""
    model = Booking
    form_class = BookingCreateForm
    template_name = 'bookings/booking_form.html'
    success_url = reverse_lazy('booking-list')
    
    def get_form_kwargs(self):
        """Pass the current user to the form"""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        """Process the valid form data"""
        booking = form.instance
        booking.user = self.request.user
        booking.total_price = form.calculated_price
        booking.status = 'pending'
        
        messages.success(self.request, 'Бронювання успішно створено та очікує підтвердження.')
        return super().form_valid(form)

class BookingUpdateView(LoginRequiredMixin, UpdateView):
    """View for updating a booking"""
    model = Booking
    form_class = BookingUpdateForm
    template_name = 'bookings/booking_update.html'
    
    def get_queryset(self):
        """Ensure users can only update their own bookings in pending/confirmed status"""
        user = self.request.user
        if user.is_staff:
            return Booking.objects.filter(status__in=['pending', 'confirmed'])
        return Booking.objects.filter(
            user=user,
            status__in=['pending', 'confirmed']
        )
    
    def get_success_url(self):
        """Return to booking detail page after update"""
        return reverse('booking-detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        """Process the valid form data"""
        booking = form.instance
        booking.total_price = form.calculated_price
        
        # Create history record
        BookingHistory.objects.create(
            booking=booking,
            status=booking.status,
            notes="Бронювання оновлено користувачем"
        )
        
        messages.success(self.request, 'Бронювання успішно оновлено.')
        return super().form_valid(form)

@login_required
def cancel_booking(request, pk):
    """Cancel a booking"""
    booking = get_object_or_404(Booking, pk=pk)
    
    # Check permissions
    if not request.user.is_staff and booking.user != request.user:
        return HttpResponseForbidden("У вас немає доступу до цього бронювання.")
    
    # Check if cancellation is possible
    if booking.status not in ['pending', 'confirmed']:
        messages.error(request, "Це бронювання не можна скасувати.")
        return redirect('booking-detail', pk=booking.pk)
    
    if request.method == 'POST':
        form = BookingCancelForm(request.POST)
        if form.is_valid():
            # Cancel the booking
            booking.status = 'cancelled'
            booking.save()
            
            # Create a history record
            BookingHistory.objects.create(
                booking=booking,
                status='cancelled',
                notes="Бронювання скасовано користувачем"
            )
            
            # Update car status if needed
            if booking.car.status == 'busy':
                booking.car.status = 'available'
                booking.car.save()
            
            messages.success(request, "Бронювання успішно скасовано.")
            return redirect('booking-list')
    else:
        form = BookingCancelForm()
    
    return render(request, 'bookings/cancel_booking.html', {
        'booking': booking,
        'form': form
    })

@login_required
def start_rental(request):
    """Start a car rental"""
    if request.method == 'POST':
        form = BookingStartRentalForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user
            car = form.cleaned_data['car']
            
            # Отримуємо координати початку оренди
            pickup_lat = form.cleaned_data.get("latitude")
            pickup_lng = form.cleaned_data.get("longitude")
            
            # Створюємо новий запис бронювання
            now = timezone.now()
            pickup_location = ""
            
            if pickup_lat and pickup_lng:
                pickup_location = f"{pickup_lat},{pickup_lng}"
                
                # Оновлюємо поточне місцезнаходження автомобіля
                car.current_latitude = str(pickup_lat)
                car.current_longitude = str(pickup_lng)
                car.save()

            booking = Booking.objects.create(
                user=user,
                car=car,
                start_time=now,
                end_time=now + datetime.timedelta(days=1),  # Тимчасово на 24 години
                status='active',
                last_billing_time=now,
                minutes_billed=0,
                total_price=Decimal('0.00'),
                pickup_location=pickup_location
            )
            
            # Create a history record
            BookingHistory.objects.create(
                booking=booking,
                status='active',
                notes="Оренду розпочато"
            )
            
            # Update car status
            car.status = 'busy'
            car.save()
            
            messages.success(request, f"Оренда автомобіля {car} успішно розпочата!")
            return redirect('booking-detail', pk=booking.id)
    else:
        form = BookingStartRentalForm(user=request.user)
    
    return render(request, 'bookings/start_rental.html', {'form': form})

@login_required
def end_rental(request, pk):
    """End a car rental"""
    booking = get_object_or_404(Booking, pk=pk)
    
    # Check permissions
    if not request.user.is_staff and booking.user != request.user:
        return HttpResponseForbidden("У вас немає доступу до цього бронювання.")
    
    # Check if rental is active
    if booking.status != 'active':
        messages.error(request, "Ця оренда не є активною.")
        return redirect('booking-detail', pk=booking.pk)
    
    if request.method == 'POST':
        form = BookingEndRentalForm(request.POST)
        if form.is_valid():
            # End the rental
            now = timezone.now()
            
            # Отримуємо координати повернення автомобіля
            return_lat = form.cleaned_data.get("latitude")
            return_lng = form.cleaned_data.get("longitude")
            
            if return_lat and return_lng:
                # Оновлюємо місцезнаходження в записі бронювання
                booking.return_location = f"{return_lat},{return_lng}"
                
                # Оновлюємо поточне місцезнаходження автомобіля
                car = booking.car
                car.current_latitude = str(return_lat)
                car.current_longitude = str(return_lng)
                car.save()
            
            # Розрахунок останнього списання
            time_diff = now - booking.last_billing_time
            minutes_to_bill = max(1, int(time_diff.total_seconds() / 60))
            
            if minutes_to_bill > 0:
                amount_to_bill = booking.car.price_per_minute * Decimal(str(minutes_to_bill))
                
                # Зняття коштів
                try:
                    balance = booking.user.balance
                    if balance.amount >= amount_to_bill:
                        balance.amount -= amount_to_bill
                        balance.save()
                        
                        # Створення запису транзакції
                        try:
                            from payments.models import Payment, PaymentTransaction
                            
                            # Створення запису оплати бронювання
                            payment = Payment.objects.create(
                                user=booking.user,
                                amount=amount_to_bill,
                                payment_provider='internal',
                                status='completed'
                            )
                            
                            PaymentTransaction.objects.create(
                                user=booking.user,
                                payment=payment,
                                amount=amount_to_bill,
                                transaction_type='booking',
                                description=f"Оплата оренди автомобіля {booking.car}",
                                balance_after=balance.amount
                            )
                        except ImportError:
                            pass
                except:
                    pass  # Якщо недостатньо коштів, просто завершуємо оренду
                
                booking.minutes_billed += minutes_to_bill
            
            # Update booking data
            booking.status = 'completed'
            booking.end_time = now
            booking.total_price = booking.car.price_per_minute * Decimal(str(booking.minutes_billed))
            booking.save()
            
            # Create a history record
            BookingHistory.objects.create(
                booking=booking,
                status='completed',
                notes=f"Оренду завершено. Всього хвилин: {booking.minutes_billed}, загальна вартість: {booking.total_price} ₴"
            )
            
            # Update car status
            car = booking.car
            car.status = 'available'
            car.save()
            
            messages.success(request, (
                f"Оренду успішно завершено. "
                f"Всього використано: {booking.minutes_billed} хвилин. "
                f"Загальна вартість: {booking.total_price} ₴"
            ))
            return redirect('booking-list')
    else:
        form = BookingEndRentalForm()
    
    return render(request, 'bookings/end_rental.html', {
        'booking': booking,
        'form': form
    })

class AdminBookingChangeStatusView(UserPassesTestMixin, View):
    """Admin view for changing booking status"""
    
    def test_func(self):
        """Only allow staff access"""
        return self.request.user.is_staff
    
    def get(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        form = AdminBookingStatusForm(initial={'status': booking.status})
        return render(request, 'bookings/admin_change_status.html', {
            'booking': booking,
            'form': form
        })
    
    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        form = AdminBookingStatusForm(request.POST)
        
        if form.is_valid():
            new_status = form.cleaned_data['status']
            notes = form.cleaned_data['notes'] or f"Статус змінено адміністратором з {booking.status} на {new_status}"
            
            # Change booking status
            old_status = booking.status
            booking.status = new_status
            booking.save()
            
            # Create a history record
            BookingHistory.objects.create(
                booking=booking,
                status=new_status,
                notes=notes
            )
            
            # Update car status
            car = booking.car
            if new_status == 'active':
                car.status = 'busy'
            elif new_status in ['completed', 'cancelled']:
                car.status = 'available'
            car.save()
            
            messages.success(request, f"Статус бронювання змінено на {new_status}")
            return redirect('booking-detail', pk=booking.pk)
        
        return render(request, 'bookings/admin_change_status.html', {
            'booking': booking,
            'form': form
        })

class ActiveBookingsView(LoginRequiredMixin, ListView):
    """View for active bookings"""
    model = Booking
    template_name = 'bookings/active_bookings.html'
    context_object_name = 'bookings'
    
    def get_queryset(self):
        now = timezone.now()
        if self.request.user.is_staff:
            return Booking.objects.filter(
                status='active',
                start_time__lte=now,
                end_time__gte=now
            ).order_by('end_time')
        else:
            return Booking.objects.filter(
                user=self.request.user,
                status='active',
                start_time__lte=now,
                end_time__gte=now
            ).order_by('end_time')

class UpcomingBookingsView(LoginRequiredMixin, ListView):
    """View for upcoming bookings"""
    model = Booking
    template_name = 'bookings/upcoming_bookings.html'
    context_object_name = 'bookings'
    
    def get_queryset(self):
        now = timezone.now()
        if self.request.user.is_staff:
            return Booking.objects.filter(
                status__in=['pending', 'confirmed'],
                start_time__gt=now
            ).order_by('start_time')
        else:
            return Booking.objects.filter(
                user=self.request.user,
                status__in=['pending', 'confirmed'],
                start_time__gt=now
            ).order_by('start_time')