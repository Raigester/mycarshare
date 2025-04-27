from django.urls import path

from . import views


urlpatterns = [
    # Відображення платежів
    path("", views.PaymentListView.as_view(), name="payment-list"),
    path("<int:pk>/", views.PaymentDetailView.as_view(), name="payment-detail"),
    path("<int:pk>/cancel/", views.CancelPaymentActionView.as_view(), name="payment-cancel-action"),
    path("create/", views.CreatePaymentView.as_view(), name="create-payment"),
    path("process/", views.ProcessPaymentView.as_view(), name="payment-process"),
    path("success/", views.PaymentSuccessView.as_view(), name="payment-success"),
    path("cancel/", views.PaymentCancelView.as_view(), name="payment-cancel"),

    # Відображення транзакцій
    path("transactions/", views.TransactionListView.as_view(), name="transaction-list"),

    # Вебхук для зворотного виклику
    path("webhook/liqpay/", views.LiqPayCallbackView.as_view(), name="liqpay-callback"),
]
