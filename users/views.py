from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView
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

        Args:
            form: Валідована форма реєстрації користувача.

        Returns:
            HttpResponse: Перенаправлення на сторінку успіху.
        """
        form.save()
        messages.success(self.request, "Акаунт успішно створено! Тепер ви можете увійти.")
        return super().form_valid(form)

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
