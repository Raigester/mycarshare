from django.conf import settings
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView, View
from django_ratelimit.decorators import ratelimit

from .forms import (
    AdminVerificationForm,
    BalanceAddForm,
    CustomPasswordChangeForm,
    DriverLicenseVerificationForm,
    UserProfileUpdateForm,
    UserRegistrationForm,
)
from .models import DriverLicenseVerification, User, UserBalance


class UserRegistrationView(CreateView):
    """Представлення для реєстрації користувача"""
    form_class = UserRegistrationForm
    template_name = "register.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        """
        Обробляє валідну форму та зберігає дані користувача.
        Відправляє електронний лист з підтвердженням.

        Args:
            form: Валідована форма реєстрації користувача.

        Returns:
            HttpResponse: Перенаправлення на сторінку успіху.
        """
        user = form.save()

        # Send verification email
        self.send_verification_email(user)

        messages.success(
            self.request,
            "Акаунт успішно створено! Перевірте вашу електронну пошту для активації акаунту."
        )
        return super().form_valid(form)

    def send_verification_email(self, user):
        """
        Відправляє електронний лист з підтвердженням.

        Args:
            user: Користувач, якому відправляється лист.
        """
        subject = "Активація акаунту Car Sharing"
        verification_url = f"{settings.BASE_URL}/accounts/verify-email/{user.email_verification_token}/"
        message = f"""
        Вітаємо, {user.username}!

        Дякуємо за реєстрацію на нашому сервісі Car Sharing.
        Для активації вашого акаунту, будь ласка, перейдіть за посиланням нижче:

        {verification_url}

        Якщо ви не реєструвались на нашому сервісі, проігноруйте цей лист.

        З повагою,
        Команда Car Sharing
        """
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

# Захист від брутфорсу обмеження кількості запитів до 3 разів на 5 хвилин
@method_decorator(ratelimit(key="ip", rate="3/5m", method="POST", block=True), name="dispatch")
class CustomLoginView(LoginView):
    """Представлення для входу користувача"""
    template_name = "login.html"

    def dispatch(self, request, *args, **kwargs):
        """
        Перевіряє, чи користувач вже автентифікований, і перенаправляє на профіль якщо так.

        Args:
            request: HTTP запит.
            *args: Додаткові позиційні аргументи.
            **kwargs: Додаткові іменовані аргументи.

        Returns:
            HttpResponse: Перенаправлення на профіль або стандартна обробка запиту.
        """
        if request.user.is_authenticated:
            return redirect("profile")
        return super().dispatch(request, *args, **kwargs)

class UserProfileView(LoginRequiredMixin, UpdateView):
    """Представлення для профілю користувача"""
    model = User
    form_class = UserProfileUpdateForm
    template_name = "profile.html"
    success_url = reverse_lazy("profile")

    def get_object(self):
        """
        Отримує об'єкт користувача для редагування.

        Returns:
            User: Поточний аутентифікований користувач.
        """
        return self.request.user

    def form_valid(self, form):
        """
        Обробляє валідну форму оновлення профілю.

        Args:
            form: Валідована форма оновлення профілю.

        Returns:
            HttpResponse: Перенаправлення на сторінку успіху.
        """
        messages.success(self.request, "Ваш профіль успішно оновлено!")
        return super().form_valid(form)

@login_required
def change_password_view(request):
    """
    Представлення для зміни пароля користувача.

    Args:
        request: HTTP запит.

    Returns:
        HttpResponse: Рендер сторінки зміни пароля або перенаправлення на профіль.
    """
    if request.method == "POST":
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Залишити користувача в системі
            messages.success(request, "Ваш пароль успішно змінено!")
            return redirect("profile")
        else:
            messages.error(request, "Будь ласка, виправте помилки нижче.")
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, "change_password.html", {"form": form})

class DriverLicenseVerificationCreateView(LoginRequiredMixin, CreateView):
    """Представлення для створення запиту на верифікацію водійських прав"""
    model = DriverLicenseVerification
    form_class = DriverLicenseVerificationForm
    template_name = "driver_verification_form.html"
    success_url = reverse_lazy("verification-list")

    def dispatch(self, request, *args, **kwargs):
        """
        Перевіряє, чи користувач вже має активну заявку на верифікацію.

        Args:
            request: HTTP запит.
            *args: Додаткові позиційні аргументи.
            **kwargs: Додаткові іменовані аргументи.

        Returns:
            HttpResponse: Перенаправлення на список заявок або стандартна обробка запиту.
        """
        active_verification = DriverLicenseVerification.objects.filter(
            user=request.user,
        ).exclude(status="rejected").order_by("-created_at").first()

        if active_verification:
            messages.error(
                request,
                "Ви вже маєте схвалену заявку на верифікацію або ваша заявка в очікуванні розгляду."
            )
            return redirect("verification-list")

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        Обробляє валідну форму та зберігає заявку на верифікацію.

        Args:
            form: Валідована форма верифікації.

        Returns:
            HttpResponse: Перенаправлення на сторінку успіху.
        """
        form.instance.user = self.request.user
        messages.success(self.request, "Ваш запит на верифікацію водійських прав надіслано!")
        return super().form_valid(form)


class DriverLicenseVerificationListView(LoginRequiredMixin, ListView):
    """Представлення для відображення списку запитів на верифікацію водійських прав користувача"""
    model = DriverLicenseVerification
    template_name = "driver_verification_list.html"
    context_object_name = "verifications"

    def get_queryset(self):
        """
        Отримує список заявок на верифікацію для поточного користувача.

        Returns:
            QuerySet: Об'єкти верифікації для поточного користувача.
        """
        return DriverLicenseVerification.objects.filter(user=self.request.user)

class AdminVerificationListView(UserPassesTestMixin, ListView):
    """Представлення для адміністратора для перегляду запитів на верифікацію"""
    model = DriverLicenseVerification
    template_name = "admin_verification_list.html"
    context_object_name = "verifications"

    def test_func(self):
        """
        Перевіряє, чи користувач має права адміністратора.

        Returns:
            bool: True, якщо користувач є адміністратором, інакше False.
        """
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        """
        Отримує контекстні дані для шаблону, включаючи відфільтровані списки заявок.

        Args:
            **kwargs: Додаткові іменовані аргументи.

        Returns:
            dict: Контекстні дані для шаблону.
        """
        context = super().get_context_data(**kwargs)
        context["pending_verifications"] = DriverLicenseVerification.objects.filter(
            status="pending"
        ).order_by("-created_at")
        context["approved_verifications"] = DriverLicenseVerification.objects.filter(
            status="approved"
        ).order_by("-created_at")
        context["rejected_verifications"] = DriverLicenseVerification.objects.filter(
            status="rejected"
        ).order_by("-created_at")
        return context

class AdminVerificationUpdateView(UserPassesTestMixin, UpdateView):
    """Представлення адміністратора для оновлення запиту на верифікацію"""
    model = DriverLicenseVerification
    form_class = AdminVerificationForm
    template_name = "admin_verification_detail.html"
    success_url = reverse_lazy("admin-verification-list")

    def test_func(self):
        """
        Перевіряє, чи користувач має права адміністратора.

        Returns:
            bool: True, якщо користувач є адміністратором, інакше False.
        """
        return self.request.user.is_staff

    def form_valid(self, form):
        """
        Обробляє валідну форму та оновлює статус заявки на верифікацію.

        Args:
            form: Валідована форма адміністратора.

        Returns:
            HttpResponse: Перенаправлення на сторінку успіху.
        """
        verification = form.save()

        # Якщо верифікація схвалена, оновити статус користувача
        if verification.status == "approved":
            user = verification.user
            user.is_verified_driver = True
            user.save()
            messages.success(self.request, f"Верифікація водія для {user.username} схвалена!")
        elif verification.status == "rejected":
            messages.info(self.request, f"Верифікація водія для {verification.user.username} відхилена.")

        return super().form_valid(form)

@login_required
def user_balance_view(request):
    """
    Представлення для відображення та поповнення балансу користувача.

    Args:
        request: HTTP запит.

    Returns:
        HttpResponse: Рендер сторінки балансу або перенаправлення на цю ж сторінку.
    """
    # Отримати або створити баланс користувача
    balance, created = UserBalance.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = BalanceAddForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data["amount"]
            balance.amount += amount
            balance.save()
            messages.success(request, f"Успішно додано {amount} до вашого балансу!")
            return redirect("balance")
    else:
        form = BalanceAddForm()

    return render(request, "balance.html", {
        "balance": balance,
        "form": form
    })




class EmailVerificationView(View):
    """Представлення для верифікації електронної пошти"""

    def get(self, request, token):
        """
        Обробляє запит на верифікацію електронної пошти.

        Args:
            request: HTTP запит.
            token: Токен верифікації.

        Returns:
            HttpResponse: Перенаправлення на сторінку входу.
        """
        try:
            user = User.objects.get(email_verification_token=token)
            user.is_email_verified = True
            user.is_active = True
            user.save()
            messages.success(request, "Ваш акаунт успішно активовано! Тепер ви можете увійти.")
        except User.DoesNotExist:
            messages.error(request, "Недійсний токен активації.")

        return redirect("login")

def resend_verification_email(request):
    """
    Повторно відправляє електронний лист з підтвердженням.

    Args:
        request: HTTP запит.

    Returns:
        HttpResponse: Рендер сторінки повторної відправки або перенаправлення.
    """
    if request.method == "POST":
        email = request.POST.get("email")
        try:
            user = User.objects.get(email=email)
            if user.is_email_verified:
                messages.info(request, "Цей акаунт вже активовано.")
                return redirect("login")

            subject = "Активація акаунту Car Sharing"
            verification_url = f"{settings.BASE_URL}/accounts/verify-email/{user.email_verification_token}/"
            message = f"""
            Вітаємо, {user.username}!

            Дякуємо за реєстрацію на нашому сервісі Car Sharing.
            Для активації вашого акаунту, будь ласка, перейдіть за посиланням нижче:

            {verification_url}

            Якщо ви не реєструвались на нашому сервісі, проігноруйте цей лист.

            З повагою,
            Команда Car Sharing
            """
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )

            messages.success(
                request,
                "Лист з підтвердженням повторно надіслано. Перевірте вашу електронну пошту."
            )
            return redirect("login")
        except User.DoesNotExist:
            messages.error(request, "Користувача з таким email не знайдено.")

    return render(request, "resend_verification.html")
