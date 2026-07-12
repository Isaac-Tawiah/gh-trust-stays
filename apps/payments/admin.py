from django.contrib import admin
from .models import Payment, Payout


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'booking', 'amount', 'method', 'status', 'paystack_reference', 'created_at')
    list_filter = ('status', 'method', 'created_at')
    search_fields = ('user__first_name', 'paystack_reference')


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ('id', 'host', 'booking', 'amount', 'platform_fee', 'net_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('host__first_name',)