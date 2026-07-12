from django.urls import path
from . import views

urlpatterns = [
    path('initialize/', views.initialize_payment, name='initialize-payment'),
    path('verify/<str:reference>/', views.verify_payment, name='verify-payment'),
    path('webhook/', views.paystack_webhook, name='paystack-webhook'),
    path('history/', views.payment_history, name='payment-history'),
]