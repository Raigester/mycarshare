from datetime import datetime
import json
import hashlib
import base64
import uuid
import hmac
from decimal import Decimal
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.views.generic import ListView, DetailView, FormView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
import datetime

from users.models import UserBalance
from .models import Payment, LiqPayPayment, PaymentTransaction
from .forms import CreatePaymentForm, PaymentFilterForm, TransactionFilterForm

class PaymentListView(LoginRequiredMixin, ListView):
    """View for listing user's payments"""
    
    model = Payment
    template_name = 'payment_list.html'
    context_object_name = 'payments'
    paginate_by = 10
    
    def get_queryset(self):
        """Get filtered payments for the current user or all for admin"""
        user = self.request.user
        
        # Base queryset - user's payments or all for admin
        if user.is_staff:
            queryset = Payment.objects.all()
        else:
            queryset = Payment.objects.filter(user=user)
        
        # Apply filters if form submitted
        form = PaymentFilterForm(self.request.GET)
        if form.is_valid():
            # Filter by status
            if form.cleaned_data.get('status'):
                queryset = queryset.filter(status=form.cleaned_data['status'])
            
            # Filter by payment provider
            if form.cleaned_data.get('payment_provider'):
                queryset = queryset.filter(payment_provider=form.cleaned_data['payment_provider'])
            
            # Filter by date range
            if form.cleaned_data.get('date_from'):
                queryset = queryset.filter(created_at__gte=form.cleaned_data['date_from'])
                
            if form.cleaned_data.get('date_to'):
                # Add one day to include the end date
                date_to = form.cleaned_data['date_to'] + datetime.timedelta(days=1)
                queryset = queryset.filter(created_at__lte=date_to)
                
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        """Add filter form and payment stats to context"""
        context = super().get_context_data(**kwargs)
        context['filter_form'] = PaymentFilterForm(self.request.GET)
        
        # Add payment statistics
        user = self.request.user
        
        if user.is_staff:
            payments = Payment.objects.all()
        else:
            payments = Payment.objects.filter(user=user)
            
        # Payments summary
        context['total_payments'] = payments.count()
        
        # Successful payments summary
        successful_payments = payments.filter(status='completed')
        context['total_successful'] = successful_payments.count()
        context['total_amount'] = successful_payments.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Last 30 days summary
        thirty_days_ago = timezone.now() - datetime.timedelta(days=30)
        context['recent_payments'] = successful_payments.filter(
            created_at__gte=thirty_days_ago
        ).count()
        
        context['recent_amount'] = successful_payments.filter(
            created_at__gte=thirty_days_ago
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        return context
        
class PaymentDetailView(LoginRequiredMixin, DetailView):
    """View for payment details"""
    
    model = Payment
    template_name = 'payment_detail.html'
    context_object_name = 'payment'
    
    def get_queryset(self):
        """Ensure users can only see their own payments unless they're staff"""
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(user=user)

class CreatePaymentView(LoginRequiredMixin, FormView):
    """View for creating new payments"""
    
    form_class = CreatePaymentForm
    template_name = 'create_payment.html'
    
    def form_valid(self, form):
        """Process the payment"""
        user = self.request.user
        amount = form.cleaned_data['amount']
        provider = form.cleaned_data['payment_provider']
        
        # Create the payment record
        payment = Payment.objects.create(
            user=user,
            amount=amount,
            payment_provider=provider,
            status='pending'
        )
        
        # Process payment based on provider
        if provider == 'liqpay':
            return self._create_liqpay_payment(payment)
        
        messages.error(self.request, "Непідтримуваний платіжний провайдер")
        return redirect('payment-list')
    
    def _create_liqpay_payment(self, payment):
        """Create a LiqPay payment and redirect to payment page"""
        try:
            # Generate unique order ID
            order_id = f"order_{payment.id}_{payment.user.id}"
            
            # Prepare data for LiqPay
            liqpay_data = {
                'public_key': settings.LIQPAY_PUBLIC_KEY,
                'version': '3',
                'action': 'pay',
                'amount': str(payment.amount),
                'currency': 'UAH',
                'description': 'CarShare Balance Top-up',
                'order_id': order_id,
                'result_url': self.request.build_absolute_uri(reverse('payment-success')),
                'server_url': self.request.build_absolute_uri(reverse('liqpay-callback')),
            }
            
            # Convert data to JSON and then to base64
            data_json = json.dumps(liqpay_data)
            data_base64 = base64.b64encode(data_json.encode('utf-8')).decode('utf-8')
            
            # Generate signature
            signature_string = settings.LIQPAY_PRIVATE_KEY + data_base64 + settings.LIQPAY_PRIVATE_KEY
            signature = base64.b64encode(hashlib.sha1(signature_string.encode('utf-8')).digest()).decode('utf-8')
            
            # Save LiqPay payment details
            liqpay_payment = LiqPayPayment.objects.create(
                payment=payment,
                liqpay_order_id=order_id,
                liqpay_data=data_base64,
                liqpay_signature=signature
            )
            
            # Save LiqPay data in session for the template
            self.request.session['liqpay_data'] = {
                'payment_id': payment.id,
                'data': data_base64,
                'signature': signature,
            }
            
            return redirect('payment-process')
            
        except Exception as e:
            payment.status = 'failed'
            payment.save()
            messages.error(self.request, f"Помилка при створенні платежу: {str(e)}")
            return redirect('payment-list')

class ProcessPaymentView(LoginRequiredMixin, View):
    """View for processing LiqPay payment"""
    
    def get(self, request):
        """Show LiqPay payment form"""
        # Get LiqPay data from session
        liqpay_data = request.session.get('liqpay_data')
        
        if not liqpay_data:
            messages.error(request, "Дані платежу не знайдено. Будь ласка, почніть заново.")
            return redirect('create-payment')
        
        # Get payment for additional info
        try:
            payment_id = liqpay_data.get('payment_id')
            payment = Payment.objects.get(id=payment_id, user=request.user)
            
            context = {
                'payment': payment,
                'liqpay_data': liqpay_data['data'],
                'liqpay_signature': liqpay_data['signature'],
                'liqpay_form_url': 'https://www.liqpay.ua/api/3/checkout'
            }
            
            return render(request, 'process_payment.html', context)
            
        except Payment.DoesNotExist:
            messages.error(request, "Платіж не знайдено. Будь ласка, почніть заново.")
            return redirect('create-payment')

class PaymentSuccessView(LoginRequiredMixin, View):
    """Handle successful payments"""
    
    def get(self, request):
        # This view is displayed after the customer is redirected from the payment system
        messages.success(request, "Платіж обробляється. Якщо платіж був успішним, ваш баланс буде оновлено найближчим часом.")
        return redirect('payment-list')

class PaymentCancelView(LoginRequiredMixin, View):
    """Handle cancelled payments"""
    
    def get(self, request):
        messages.info(request, "Платіж було скасовано.")
        return redirect('payment-list')

@method_decorator(csrf_exempt, name='dispatch')
class LiqPayCallbackView(View):
    """Handle LiqPay callbacks"""
    
    def post(self, request):
        data = request.POST.get('data')
        signature = request.POST.get('signature')
        
        if not data or not signature:
            return HttpResponse(status=400)
        
        try:
            # Verify signature
            sign_string = settings.LIQPAY_PRIVATE_KEY + data + settings.LIQPAY_PRIVATE_KEY
            calc_signature = base64.b64encode(hashlib.sha1(sign_string.encode('utf-8')).digest()).decode('utf-8')
            
            if calc_signature != signature:
                return HttpResponse(status=400)
            
            # Decode data
            decoded_data = json.loads(base64.b64decode(data).decode('utf-8'))
            
            # Process payment
            if decoded_data.get('status') == 'success':
                order_id = decoded_data.get('order_id')
                
                try:
                    # Find payment by order ID
                    liqpay_payment = LiqPayPayment.objects.get(liqpay_order_id=order_id)
                    payment = liqpay_payment.payment
                    
                    # Skip if already processed
                    if payment.status == 'completed':
                        return HttpResponse(status=200)
                    
                    # Update payment status
                    payment.status = 'completed'
                    payment.provider_payment_id = decoded_data.get('payment_id', '')
                    payment.save()
                    
                    # Update user balance
                    self._update_user_balance(payment)
                        
                except LiqPayPayment.DoesNotExist:
                    # Payment not found, log error
                    print(f"LiqPay payment not found: {order_id}")
            
            return HttpResponse(status=200)
            
        except Exception as e:
            # Other error
            print(f"LiqPay callback error: {str(e)}")
            return HttpResponse(status=500)
    
    def _update_user_balance(self, payment):
        """Update user balance and create transaction record"""
        user = payment.user
        balance, created = UserBalance.objects.get_or_create(user=user)
        balance.amount += payment.amount
        balance.save()
        
        # Create transaction record
        PaymentTransaction.objects.create(
            user=user,
            payment=payment,
            amount=payment.amount,
            transaction_type='deposit',
            description=f"Поповнення балансу через LiqPay",
            balance_after=balance.amount
        )

class TransactionListView(LoginRequiredMixin, ListView):
    """View for listing transactions"""
    
    model = PaymentTransaction
    template_name = 'transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 15
    
    def get_queryset(self):
        """Get filtered transactions for the current user or all for admin"""
        user = self.request.user
        
        # Base queryset - user's transactions or all for admin
        if user.is_staff:
            queryset = PaymentTransaction.objects.all()
        else:
            queryset = PaymentTransaction.objects.filter(user=user)
        
        # Apply filters if form submitted
        form = TransactionFilterForm(self.request.GET)
        if form.is_valid():
            # Filter by transaction type
            if form.cleaned_data.get('transaction_type'):
                queryset = queryset.filter(transaction_type=form.cleaned_data['transaction_type'])
            
            # Filter by date range
            if form.cleaned_data.get('date_from'):
                queryset = queryset.filter(created_at__gte=form.cleaned_data['date_from'])
                
            if form.cleaned_data.get('date_to'):
                # Add one day to include the end date
                date_to = form.cleaned_data['date_to'] + datetime.timedelta(days=1)
                queryset = queryset.filter(created_at__lte=date_to)
                
        return queryset.order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        """Add filter form and transaction stats to context"""
        context = super().get_context_data(**kwargs)
        context['filter_form'] = TransactionFilterForm(self.request.GET)
        
        # Add transaction statistics
        user = self.request.user
        
        if user.is_staff:
            transactions = PaymentTransaction.objects.all()
            deposits = transactions.filter(transaction_type='deposit')
            withdrawals = transactions.filter(transaction_type='withdrawal')
        else:
            transactions = PaymentTransaction.objects.filter(user=user)
            deposits = transactions.filter(transaction_type='deposit')
            withdrawals = transactions.filter(transaction_type='withdrawal')
            
        # Transactions summary
        context['total_transactions'] = transactions.count()
        context['total_deposits'] = deposits.aggregate(
            total=Sum('amount')
        )['total'] or 0
        context['total_withdrawals'] = withdrawals.aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        # Current balance
        try:
            balance = UserBalance.objects.get(user=user).amount
        except UserBalance.DoesNotExist:
            balance = 0
        context['current_balance'] = balance
        
        return context
    
@method_decorator(csrf_exempt, name='dispatch')
class CancelPaymentActionView(LoginRequiredMixin, View):
    def post(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk, user=request.user)
        
        if payment.status != 'pending':
            messages.error(request, "Платіж вже оброблений або скасований.")
            return redirect('payment-detail', pk=pk)
        
        payment.status = 'cancelled'
        payment.save()
        
        messages.success(request, "Платіж успішно скасовано.")
        return redirect('payment-detail', pk=pk)