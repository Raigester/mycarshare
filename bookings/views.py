import datetime
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import ListView, View

from .forms import BookingEndRentalForm, BookingStartRentalForm
from .models import Booking, BookingHistory


@login_required
def start_rental(request):
    """
    Обробка початку оренди автомобіля.

    Args:
        request: Об'єкт запиту Django, що містить дані форми та інформацію про користувача.

    Returns:
        HttpResponse: Відображення сторінки форми початку оренди або перенаправлення на сторінку деталей бронювання.
    """
    car_id = request.GET.get("car")

    if request.method == "POST":
        form = BookingStartRentalForm(request.POST, user=request.user)
        if form.is_valid():
            user = request.user

            if user.is_blocked:
                messages.error(request, "Ваш обліковий запис заблоковано. Оренда неможлива.")
                return redirect("booking-list")

            latest_verification = user.license_verifications.order_by("-created_at").first()
            if not latest_verification or latest_verification.status != "approved":
                messages.error(request, "Щоб орендувати автомобіль, потрібно пройти верифікацію водійських прав.")
                return redirect("verification-create")

            car = form.cleaned_data["car"]
            pickup_lat = form.cleaned_data.get("latitude")
            pickup_lng = form.cleaned_data.get("longitude")
            now = timezone.now()
            pickup_location = ""
            if pickup_lat and pickup_lng:
                pickup_location = f"{pickup_lat},{pickup_lng}"
                car.current_latitude = str(pickup_lat)
                car.current_longitude = str(pickup_lng)
                car.save()

            booking = Booking.objects.create(
                user=user,
                car=car,
                start_time=now,
                end_time=now + datetime.timedelta(days=1),
                status="active",
                last_billing_time=now,
                minutes_billed=0,
                total_price=Decimal("0.00"),
                pickup_location=pickup_location
            )
            BookingHistory.objects.create(
                booking=booking,
                status="active",
                notes="Оренду розпочато"
            )
            car.status = "busy"
            car.save()
            messages.success(request, f"Оренда автомобіля {car} успішно розпочата!")
            return redirect("booking-detail", pk=booking.id)
    else:
        initial_data = {}
        if car_id:
            from cars.models import Car
            try:
                car = Car.objects.get(id=car_id, status="available")
                initial_data = {"car": car.id}
            except Car.DoesNotExist:
                messages.error(request, "Вибраний автомобіль недоступний для оренди.")

        form = BookingStartRentalForm(user=request.user, initial=initial_data)

    return render(request, "start_rental.html", {"form": form})

@login_required
def end_rental(request, pk):
    """
    Обробка завершення оренди автомобіля.

    Args:
        request: Об'єкт запиту Django, що містить дані форми та інформацію про користувача.
        pk: Первинний ключ бронювання, яке потрібно завершити.

    Returns:
        HttpResponse: Відображення сторінки форми завершення оренди, перенаправлення на список бронювань
                    або відповідь з забороною доступу.
    """
    booking = get_object_or_404(Booking, pk=pk)
    if not request.user.is_staff and booking.user != request.user:
        return HttpResponseForbidden("У вас немає доступу до цього бронювання.")
    if booking.status != "active":
        messages.error(request, "Ця оренда не є активною.")
        return redirect("booking-detail", pk=booking.pk)
    if request.method == "POST":
        form = BookingEndRentalForm(request.POST)
        if form.is_valid():
            now = timezone.now()
            return_lat = form.cleaned_data.get("latitude")
            return_lng = form.cleaned_data.get("longitude")
            if return_lat and return_lng:
                booking.return_location = f"{return_lat},{return_lng}"
                car = booking.car
                car.current_latitude = str(return_lat)
                car.current_longitude = str(return_lng)
                car.save()
            time_diff = now - booking.last_billing_time
            minutes_to_bill = max(1, int(time_diff.total_seconds() / 60))
            if minutes_to_bill > 0:
                amount_to_bill = booking.car.price_per_minute * Decimal(str(minutes_to_bill))
                try:
                    balance = booking.user.balance
                    if balance.amount >= amount_to_bill:
                        balance.amount -= amount_to_bill
                        balance.save()
                        from payments.models import Payment, PaymentTransaction
                        payment = Payment.objects.create(
                            user=booking.user,
                            amount=amount_to_bill,
                            payment_provider="internal",
                            status="completed"
                        )
                        PaymentTransaction.objects.create(
                            user=booking.user,
                            payment=payment,
                            amount=amount_to_bill,
                            transaction_type="booking",
                            description=f"Оплата оренди автомобіля {booking.car}",
                            balance_after=balance.amount
                        )
                except:
                    pass
                booking.minutes_billed += minutes_to_bill
            booking.status = "completed"
            booking.end_time = now
            booking.total_price = booking.car.price_per_minute * Decimal(str(booking.minutes_billed))
            booking.save()
            BookingHistory.objects.create(
                booking=booking,
                status="completed",
                notes=(
                    f"Оренду завершено. Всього хвилин: {booking.minutes_billed}, "
                    f"загальна вартість: {booking.total_price} ₴"
                )
            )
            car = booking.car
            car.status = "available"
            car.save()
            messages.success(request, (
                f"Оренду успішно завершено. "
                f"Всього використано: {booking.minutes_billed} хвилин. "
                f"Загальна вартість: {booking.total_price} ₴"
            ))
            return redirect("booking-list")
    else:
        form = BookingEndRentalForm()
    return render(request, "end_rental.html", {
        "booking": booking,
        "form": form
    })

class ActiveBookingsView(LoginRequiredMixin, ListView):
    """Представлення для відображення списку активних бронювань користувача"""
    model = Booking
    template_name = "active_bookings.html"
    context_object_name = "bookings"

    def get_queryset(self):
        """
        Отримати активні бронювання користувача, які зараз тривають.

        Args:
            self: Екземпляр класу.

        Returns:
            QuerySet: Відфільтрований QuerySet з активними бронюваннями поточного користувача.
        """
        now = timezone.now()
        return Booking.objects.filter(
            user=self.request.user,
            status="active",
            start_time__lte=now,
            end_time__gte=now
        ).order_by("end_time")

class CompletedBookingsView(LoginRequiredMixin, ListView):
    """Представлення для відображення списку завершених бронювань користувача"""
    model = Booking
    template_name = "completed_bookings.html"
    context_object_name = "bookings"

    def get_queryset(self):
        """
        Отримати завершені бронювання користувача.

        Args:
            self: Екземпляр класу.

        Returns:
            QuerySet: Відфільтрований QuerySet із завершеними бронюваннями поточного користувача.
        """
        return Booking.objects.filter(
            user=self.request.user,
            status="completed"
        ).order_by("-end_time")

class BookingDetailView(LoginRequiredMixin, View):
    """Представлення для відображення деталей конкретного бронювання"""
    def get(self, request, pk):
        """
        Отримати деталі бронювання та історію змін.

        Args:
            self: Екземпляр класу.
            request: Об'єкт запиту Django, що містить інформацію про користувача.
            pk: Первинний ключ бронювання, деталі якого потрібно отримати.

        Returns:
            HttpResponse: Відображення сторінки з деталями бронювання або відповідь з забороною доступу.
        """
        booking = get_object_or_404(Booking, pk=pk)
        if not request.user.is_staff and booking.user != request.user:
            return HttpResponseForbidden("У вас немає доступу до цього бронювання.")
        history = BookingHistory.objects.filter(booking=booking).order_by("-timestamp")
        return render(request, "booking_detail.html", {
            "booking": booking,
            "history": history
        })
