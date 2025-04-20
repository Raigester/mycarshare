from datetime import datetime
import json
import hashlib
import base64
import uuid
import hmac
from decimal import Decimal
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.urls import reverse
from rest_framework import viewsets, generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action

from users.models import UserBalance
from .models import Payment, WayForPayPayment, LiqPayPayment, PaymentTransaction
from .serializers import (
    PaymentSerializer, CreatePaymentSerializer, PaymentTransactionSerializer
)

class PaymentViewSet(viewsets.ModelViewSet):
    """API endpoint for payments"""
    
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users see only their own payments, admins see all
        user = self.request.user
        if not user.is_authenticated:
            return Payment.objects.none()
        if user.is_staff:
            return Payment.objects.all()
        return Payment.objects.filter(user=user)
    
    def create(self, request):
        """Create new payment"""
        serializer = CreatePaymentSerializer(data=request.data)
        
        if serializer.is_valid():
            amount = serializer.validated_data['amount']
            provider = serializer.validated_data['payment_provider']
            
            # Create the payment record
            payment = Payment.objects.create(
                user=request.user,
                amount=amount,
                payment_provider=provider,
                status='pending'
            )
            
            # Process payment based on provider
            if provider == 'liqpay':
                return self._create_liqpay_payment(payment, request)
            elif provider == 'wayforpay':
                return self._create_wayforpay_payment(payment, request)
            
            return Response(
                {"error": "Unsupported payment provider"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _create_liqpay_payment(self, payment, request):
        """Create a LiqPay payment"""
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
                'result_url': request.build_absolute_uri(reverse('payment-success')),
                'server_url': request.build_absolute_uri(reverse('liqpay-callback')),
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
            
            return Response({
                'payment_id': payment.id,
                'liqpay_checkout_data': {
                    'data': data_base64,
                    'signature': signature
                },
                'liqpay_form_url': 'https://www.liqpay.ua/api/3/checkout'
            })
            
        except Exception as e:
            payment.status = 'failed'
            payment.save()
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def _create_wayforpay_payment(self, payment, request):
        """Create a WayForPay payment"""
        try:
            # Generate unique order ID
            order_id = f"CARSHARE-{payment.id}-{uuid.uuid4().hex[:8]}"
            
            # Current timestamp
            order_date = int(payment.created_at.timestamp())
            
            # Prepare data for WayForPay
            wayforpay_data = {
                'merchantAccount': settings.WAYFORPAY_MERCHANT_ACCOUNT,
                'merchantDomainName': settings.WAYFORPAY_MERCHANT_DOMAIN,
                'merchantTransactionSecureType': 'AUTO',
                'orderReference': order_id,
                'orderDate': order_date,
                'amount': str(payment.amount),
                'currency': 'UAH',
                'productName': ['CarShare Balance Top-up'],
                'productPrice': [str(payment.amount)],
                'productCount': [1],
                'merchantTransactionType': 'CHARGE',
                'returnUrl': request.build_absolute_uri(reverse('payment-success')),
                'serviceUrl': request.build_absolute_uri(reverse('wayforpay-callback')),
                'language': 'UA'
            }
            
            # Add user info if available
            user = payment.user
            if user.email:
                wayforpay_data['email'] = user.email
            if user.phone_number:
                wayforpay_data['phone'] = user.phone_number
            if user.first_name and user.last_name:
                wayforpay_data['clientName'] = f"{user.first_name} {user.last_name}"
            
            # Generate signature
            signature_fields = [
                wayforpay_data['merchantAccount'],
                wayforpay_data['merchantDomainName'],
                wayforpay_data['orderReference'],
                str(wayforpay_data['orderDate']),
                str(wayforpay_data['amount']),
                wayforpay_data['currency'],
                wayforpay_data['productName'][0],
                str(wayforpay_data['productCount'][0]),
                str(wayforpay_data['productPrice'][0])
            ]
            signature_str = ';'.join(signature_fields)
            signature = hmac.new(
                settings.WAYFORPAY_MERCHANT_SECRET.encode('utf-8'),
                signature_str.encode('utf-8'),
                hashlib.md5
            ).hexdigest()
            
            wayforpay_data['merchantSignature'] = signature
            
            # Save WayForPay payment details
            wayforpay_payment = WayForPayPayment.objects.create(
                payment=payment,
                wayforpay_order_id=order_id,
                wayforpay_signature=signature
            )
            
            return Response({
                'payment_id': payment.id,
                'wayforpay_checkout_data': wayforpay_data,
                'wayforpay_form_url': 'https://secure.wayforpay.com/pay'
            })
            
        except Exception as e:
            payment.status = 'failed'
            payment.save()
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class PaymentTransactionViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for payment transactions"""
    
    serializer_class = PaymentTransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users see only their own transactions, admins see all
        user = self.request.user
        if not user.is_authenticated:
            return PaymentTransaction.objects.none()
        if user.is_staff:
            return PaymentTransaction.objects.all()
        return PaymentTransaction.objects.filter(user=user)

class PaymentSuccessView(APIView):
    """Handle successful payments"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # This view is called after user is redirected from payment gateway
        # We just show a success message, actual payment processing 
        # happens in webhook callbacks
        return Response({
            "message": "Payment was processed. If payment was successful, your balance will be updated shortly."
        })

class PaymentCancelView(APIView):
    """Handle cancelled payments"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        return Response({
            "message": "Payment was cancelled",
        })

@method_decorator(csrf_exempt, name='dispatch')
class LiqPayCallbackView(APIView):
    """Handle LiqPay callbacks"""
    
    permission_classes = [permissions.AllowAny]
    
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
            description=f"Balance top-up via LiqPay",
            balance_after=balance.amount
        )

@method_decorator(csrf_exempt, name='dispatch')
class WayForPayCallbackView(APIView):
    """Handle WayForPay callbacks"""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        try:
            # Parse JSON data from request
            data = json.loads(request.body.decode('utf-8'))
            
            # Validate the request
            if 'orderReference' not in data or 'merchantSignature' not in data:
                return HttpResponse(json.dumps({
                    'orderReference': data.get('orderReference', ''),
                    'status': 'failure',
                    'time': int(datetime.now().timestamp())
                }), content_type='application/json', status=400)
            
            # Verify signature
            received_signature = data['merchantSignature']
            order_reference = data['orderReference']
            transaction_status = data.get('transactionStatus', '')
            
            # Find the payment
            try:
                from datetime import datetime
                
                wayforpay_payment = WayForPayPayment.objects.get(wayforpay_order_id=order_reference)
                payment = wayforpay_payment.payment
                
                # Skip if already processed
                if payment.status == 'completed':
                    return self._generate_response(order_reference, 'success')
                
                # Check if the payment is approved
                if transaction_status == 'Approved':
                    # Calculate signature for validation
                    signature_fields = [
                        settings.WAYFORPAY_MERCHANT_ACCOUNT,
                        order_reference,
                        transaction_status
                    ]
                    signature_str = ';'.join(signature_fields)
                    calculated_signature = hmac.new(
                        settings.WAYFORPAY_MERCHANT_SECRET.encode('utf-8'),
                        signature_str.encode('utf-8'),
                        hashlib.md5
                    ).hexdigest()
                    
                    if calculated_signature != received_signature:
                        return self._generate_response(order_reference, 'failure')
                    
                    # Update payment details
                    payment.status = 'completed'
                    payment.provider_payment_id = data.get('orderReference', '')
                    payment.save()
                    
                    # Update WayForPay payment details
                    wayforpay_payment.wayforpay_transaction_id = data.get('transactionId', '')
                    wayforpay_payment.wayforpay_status = transaction_status
                    wayforpay_payment.save()
                    
                    # Update user balance
                    self._update_user_balance(payment)
                    
                    return self._generate_response(order_reference, 'success')
                
                return self._generate_response(order_reference, 'failure')
                
            except WayForPayPayment.DoesNotExist:
                return self._generate_response(order_reference, 'failure')
            
        except Exception as e:
            print(f"WayForPay callback error: {str(e)}")
            return HttpResponse(status=500)
    
    def _generate_response(self, order_reference, status):
        """Generate response for WayForPay"""
        response_data = {
            'orderReference': order_reference,
            'status': status,
            'time': int(datetime.now().timestamp())
        }
        
        # Generate signature
        signature_fields = [
            settings.WAYFORPAY_MERCHANT_ACCOUNT,
            order_reference,
            status
        ]
        signature_str = ';'.join(signature_fields)
        signature = hmac.new(
            settings.WAYFORPAY_MERCHANT_SECRET.encode('utf-8'),
            signature_str.encode('utf-8'),
            hashlib.md5
        ).hexdigest()
        
        response_data['merchantSignature'] = signature
        
        return HttpResponse(
            json.dumps(response_data),
            content_type='application/json'
        )
    
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
            description=f"Balance top-up via WayForPay",
            balance_after=balance.amount
        )
