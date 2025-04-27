import base64
import datetime
import hashlib
import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, FormView, ListView, View

from users.models import UserBalance

from .forms import CreatePaymentForm, PaymentFilterForm, TransactionFilterForm
from .models import LiqPayPayment, Payment, PaymentTransaction


class PaymentListView(LoginRequiredMixin, ListView):
    """Представлення списку платежів користувача"""

    model = Payment
    template_name = "payment_list.html"
    context_object_name = "payments"
    paginate_by = 10

    def get_queryset(self):
        """
        Отримати відфільтровані платежі для поточного користувача або всі для адміністратора.

        Args:
            self: Екземпляр класу.

        Returns:
            QuerySet: Відфільтрований та відсортований QuerySet об'єктів Payment.
        """
        user = self.request.user

        # Базовий запит - платежі користувача або всі для адміністратора
        if user.is_staff:
            queryset = Payment.objects.all()
        else:
            queryset = Payment.objects.filter(user=user)

        # Застосувати фільтри, якщо форма була відправлена
        form = PaymentFilterForm(self.request.GET)
        if form.is_valid():
            # Фільтр за статусом
            if form.cleaned_data.get("status"):
                queryset = queryset.filter(status=form.cleaned_data["status"])

            # Фільтр за провайдером платежу
            if form.cleaned_data.get("payment_provider"):
                queryset = queryset.filter(payment_provider=form.cleaned_data["payment_provider"])

            # Фільтр за діапазоном дат
            if form.cleaned_data.get("date_from"):
                queryset = queryset.filter(created_at__gte=form.cleaned_data["date_from"])

            if form.cleaned_data.get("date_to"):
                # Додати один день, щоб включити кінцеву дату
                date_to = form.cleaned_data["date_to"] + datetime.timedelta(days=1)
                queryset = queryset.filter(created_at__lte=date_to)

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        """
        Додати форму фільтрації та статистику платежів до контексту.

        Args:
            self: Екземпляр класу.
            **kwargs: Додаткові іменовані аргументи.

        Returns:
            dict: Контекстні дані для шаблону, включаючи форму фільтрації та статистику платежів.
        """
        context = super().get_context_data(**kwargs)
        context["filter_form"] = PaymentFilterForm(self.request.GET)

        # Додати статистику платежів
        user = self.request.user

        if user.is_staff:
            payments = Payment.objects.all()
        else:
            payments = Payment.objects.filter(user=user)

        # Загальна кількість платежів
        context["total_payments"] = payments.count()

        # Загальна кількість успішних платежів
        successful_payments = payments.filter(status="completed")
        context["total_successful"] = successful_payments.count()
        context["total_amount"] = successful_payments.aggregate(
            total=Sum("amount")
        )["total"] or 0

        # Статистика за останні 30 днів
        thirty_days_ago = timezone.now() - datetime.timedelta(days=30)
        context["recent_payments"] = successful_payments.filter(
            created_at__gte=thirty_days_ago
        ).count()

        context["recent_amount"] = successful_payments.filter(
            created_at__gte=thirty_days_ago
        ).aggregate(total=Sum("amount"))["total"] or 0

        return context

class PaymentDetailView(LoginRequiredMixin, DetailView):
    """Представлення деталей платежу"""

    model = Payment
    template_name = "payment_detail.html"
    context_object_name = "payment"

    def get_queryset(self):
        """
        Переконатися, що користувачі можуть бачити лише свої платежі, якщо вони не є адміністраторами.

        Args:
            self: Екземпляр класу.

        Returns:
            QuerySet: QuerySet об'єктів Payment, відфільтрований за правами доступу.
        """
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(user=user)

class CreatePaymentView(LoginRequiredMixin, FormView):
    """Представлення для створення нових платежів"""

    form_class = CreatePaymentForm
    template_name = "create_payment.html"

    def form_valid(self, form):
        """
        Обробка платежу після валідації форми.

        Args:
            self: Екземпляр класу.
            form: Екземпляр форми з валідованими даними.

        Returns:
            HttpResponse: Перенаправлення на відповідну сторінку в залежності від результату обробки.
        """
        user = self.request.user
        amount = form.cleaned_data["amount"]
        provider = form.cleaned_data["payment_provider"]

        # Створити запис платежу
        payment = Payment.objects.create(
            user=user,
            amount=amount,
            payment_provider=provider,
            status="pending"
        )

        # Обробка платежу залежно від провайдера
        if provider == "liqpay":
            return self._create_liqpay_payment(payment)

        messages.error(self.request, "Непідтримуваний платіжний провайдер")
        return redirect("payment-list")

    def _create_liqpay_payment(self, payment):
        """
        Створити платіж LiqPay і перенаправити на сторінку платежу.

        Args:
            self: Екземпляр класу.
            payment: Об'єкт Payment, для якого створюється платіж LiqPay.

        Returns:
            HttpResponse: Перенаправлення на сторінку обробки платежу або на список платежів у разі помилки.
        """
        try:
            # Згенерувати унікальний ідентифікатор замовлення
            order_id = f"order_{payment.id}_{payment.user.id}"

            # Підготувати дані для LiqPay
            liqpay_data = {
                "public_key": settings.LIQPAY_PUBLIC_KEY,
                "version": "3",
                "action": "pay",
                "amount": str(payment.amount),
                "currency": "UAH",
                "description": "CarShare Balance Top-up",
                "order_id": order_id,
                "result_url": self.request.build_absolute_uri(reverse("payment-success")),
                "server_url": self.request.build_absolute_uri(reverse("liqpay-callback")),
            }

            # Перетворити дані в JSON, а потім в base64
            data_json = json.dumps(liqpay_data)
            data_base64 = base64.b64encode(data_json.encode("utf-8")).decode("utf-8")

            # Згенерувати підпис
            signature_string = settings.LIQPAY_PRIVATE_KEY + data_base64 + settings.LIQPAY_PRIVATE_KEY
            signature = base64.b64encode(hashlib.sha1(signature_string.encode("utf-8")).digest()).decode("utf-8")

            # Зберегти деталі платежу LiqPay
            LiqPayPayment.objects.create(
                payment=payment,
                liqpay_order_id=order_id,
                liqpay_data=data_base64,
                liqpay_signature=signature
            )

            # Зберегти дані LiqPay в сесії для шаблону
            self.request.session["liqpay_data"] = {
                "payment_id": payment.id,
                "data": data_base64,
                "signature": signature,
            }

            return redirect("payment-process")

        except Exception as e:
            payment.status = "failed"
            payment.save()
            messages.error(self.request, f"Помилка при створенні платежу: {str(e)}")
            return redirect("payment-list")

class ProcessPaymentView(LoginRequiredMixin, View):
    """Представлення для обробки платежу через LiqPay"""

    def get(self, request):
        """
        Показати форму платежу LiqPay.

        Args:
            self: Екземпляр класу.
            request: Об'єкт HTTP запиту.

        Returns:
            HttpResponse: Рендер сторінки обробки платежу або перенаправлення у разі помилки.
        """
        # Отримати дані LiqPay із сесії
        liqpay_data = request.session.get("liqpay_data")

        if not liqpay_data:
            messages.error(request, "Дані платежу не знайдено. Будь ласка, почніть заново.")
            return redirect("create-payment")

        # Отримати платіж для додаткової інформації
        try:
            payment_id = liqpay_data.get("payment_id")
            payment = Payment.objects.get(id=payment_id, user=request.user)

            context = {
                "payment": payment,
                "liqpay_data": liqpay_data["data"],
                "liqpay_signature": liqpay_data["signature"],
                "liqpay_form_url": "https://www.liqpay.ua/api/3/checkout"
            }

            return render(request, "process_payment.html", context)

        except Payment.DoesNotExist:
            messages.error(request, "Платіж не знайдено. Будь ласка, почніть заново.")
            return redirect("create-payment")

class PaymentSuccessView(LoginRequiredMixin, View):
    """Обробка успішних платежів"""

    def get(self, request):
        """
        Обробка повернення користувача після успішного платежу.

        Args:
            self: Екземпляр класу.
            request: Об'єкт HTTP запиту.

        Returns:
            HttpResponse: Перенаправлення на список платежів з повідомленням про успіх.
        """
        # Це повідомлення показується після того, як клієнт перенаправлений із платіжної системи
        messages.success(
            request,
            "Платіж обробляється. Якщо платіж був успішним, ваш баланс буде оновлено "
            "найближчим часом."
        )
        return redirect("payment-list")

class PaymentCancelView(LoginRequiredMixin, View):
    """Обробка скасованих платежів"""

    def get(self, request):
        """
        Обробка повернення користувача після скасування платежу.

        Args:
            self: Екземпляр класу.
            request: Об'єкт HTTP запиту.

        Returns:
            HttpResponse: Перенаправлення на список платежів з інформаційним повідомленням.
        """
        messages.info(request, "Платіж було скасовано.")
        return redirect("payment-list")

@method_decorator(csrf_exempt, name="dispatch")
class LiqPayCallbackView(View):
    """Обробка зворотних викликів LiqPay"""

    def post(self, request):
        """
        Обробка зворотних викликів від LiqPay.

        Args:
            self: Екземпляр класу.
            request: Об'єкт HTTP запиту.

        Returns:
            HttpResponse: HTTP відповідь із відповідним статус-кодом.
        """
        data = request.POST.get("data")
        signature = request.POST.get("signature")

        if not data or not signature:
            return HttpResponse(status=400)

        try:
            # Перевірити підпис
            sign_string = settings.LIQPAY_PRIVATE_KEY + data + settings.LIQPAY_PRIVATE_KEY
            calc_signature = base64.b64encode(hashlib.sha1(sign_string.encode("utf-8")).digest()).decode("utf-8")

            if calc_signature != signature:
                return HttpResponse(status=400)

            # Розшифрувати дані
            decoded_data = json.loads(base64.b64decode(data).decode("utf-8"))

            # Обробити платіж
            if decoded_data.get("status") == "success":
                order_id = decoded_data.get("order_id")

                try:
                    # Знайти платіж за ідентифікатором замовлення
                    liqpay_payment = LiqPayPayment.objects.get(liqpay_order_id=order_id)
                    payment = liqpay_payment.payment

                    # Пропустити, якщо вже оброблено
                    if payment.status == "completed":
                        return HttpResponse(status=200)

                    # Оновити статус платежу
                    payment.status = "completed"
                    payment.save()

                    # Оновити баланс користувача
                    self._update_user_balance(payment)

                except LiqPayPayment.DoesNotExist:
                    # Платіж не знайдено, записати помилку
                    print(f"LiqPay payment not found: {order_id}")

            return HttpResponse(status=200)

        except Exception as e:
            # Інша помилка
            print(f"LiqPay callback error: {str(e)}")
            return HttpResponse(status=500)

    def _update_user_balance(self, payment):
        """
        Оновити баланс користувача та створити запис транзакції.

        Args:
            self: Екземпляр класу.
            payment: Об'єкт Payment, для якого оновлюється баланс.

        Returns:
            None: Функція не повертає значення.
        """
        user = payment.user
        balance, created = UserBalance.objects.get_or_create(user=user)
        balance.amount += payment.amount
        balance.save()

        # Створити запис транзакції
        PaymentTransaction.objects.create(
            user=user,
            payment=payment,
            amount=payment.amount,
            transaction_type="deposit",
            description="Поповнення балансу через LiqPay",
            balance_after=balance.amount
        )

class TransactionListView(LoginRequiredMixin, ListView):
    """Представлення списку транзакцій"""

    model = PaymentTransaction
    template_name = "transaction_list.html"
    context_object_name = "transactions"
    paginate_by = 15

    def get_queryset(self):
        """
        Отримати відфільтровані транзакції для поточного користувача або всі для адміністратора.

        Args:
            self: Екземпляр класу.

        Returns:
            QuerySet: Відфільтрований та відсортований QuerySet об'єктів PaymentTransaction.
        """
        user = self.request.user

        # Базовий запит - транзакції користувача або всі для адміністратора
        if user.is_staff:
            queryset = PaymentTransaction.objects.all()
        else:
            queryset = PaymentTransaction.objects.filter(user=user)

        # Застосувати фільтри, якщо форма була відправлена
        form = TransactionFilterForm(self.request.GET)
        if form.is_valid():
            # Фільтр за типом транзакції
            if form.cleaned_data.get("transaction_type"):
                queryset = queryset.filter(transaction_type=form.cleaned_data["transaction_type"])

            # Фільтр за діапазоном дат
            if form.cleaned_data.get("date_from"):
                queryset = queryset.filter(created_at__gte=form.cleaned_data["date_from"])

            if form.cleaned_data.get("date_to"):
                # Додати один день, щоб включити кінцеву дату
                date_to = form.cleaned_data["date_to"] + datetime.timedelta(days=1)
                queryset = queryset.filter(created_at__lte=date_to)

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        """
        Додати форму фільтрації та статистику транзакцій до контексту.

        Args:
            self: Екземпляр класу.
            **kwargs: Додаткові іменовані аргументи.

        Returns:
            dict: Контекстні дані для шаблону, включаючи форму фільтрації та статистику транзакцій.
        """
        context = super().get_context_data(**kwargs)
        context["filter_form"] = TransactionFilterForm(self.request.GET)

        # Додати статистику транзакцій
        user = self.request.user

        if user.is_staff:
            transactions = PaymentTransaction.objects.all()
            deposits = transactions.filter(transaction_type="deposit")
            withdrawals = transactions.filter(transaction_type="withdrawal")
        else:
            transactions = PaymentTransaction.objects.filter(user=user)
            deposits = transactions.filter(transaction_type="deposit")
            withdrawals = transactions.filter(transaction_type="withdrawal")

        # Загальна кількість транзакцій
        context["total_transactions"] = transactions.count()
        context["total_deposits"] = deposits.aggregate(
            total=Sum("amount")
        )["total"] or 0
        context["total_withdrawals"] = withdrawals.aggregate(
            total=Sum("amount")
        )["total"] or 0

        # Поточний баланс
        try:
            balance = UserBalance.objects.get(user=user).amount
        except UserBalance.DoesNotExist:
            balance = 0
        context["current_balance"] = balance

        return context

@method_decorator(csrf_exempt, name="dispatch")
class CancelPaymentActionView(LoginRequiredMixin, View):
    def post(self, request, pk):
        """
        Обробка POST-запиту для скасування платежу.

        Args:
            self: Екземпляр класу.
            request: Об'єкт HTTP запиту.
            pk: Первинний ключ платежу, який потрібно скасувати.

        Returns:
            HttpResponse: Перенаправлення на деталі платежу з відповідним повідомленням.
        """
        payment = get_object_or_404(Payment, pk=pk, user=request.user)

        if payment.status != "pending":
            messages.error(request, "Платіж вже оброблений або скасований.")
            return redirect("payment-detail", pk=pk)

        payment.status = "cancelled"
        payment.save()

        messages.success(request, "Платіж успішно скасовано.")
        return redirect("payment-detail", pk=pk)
