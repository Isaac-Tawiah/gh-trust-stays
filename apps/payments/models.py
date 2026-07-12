import uuid
from django.db import models
from django.conf import settings
from apps.properties.models import Booking


class Payment(models.Model):

    class PaymentMethod(models.TextChoices):
        MOMO = 'MOMO', 'Mobile Money'
        CARD = 'CARD', 'Credit/Debit Card'
        BANK = 'BANK', 'Bank Transfer'

    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SUCCESS = 'SUCCESS', 'Successful'
        FAILED = 'FAILED', 'Failed'
        REFUNDED = 'REFUNDED', 'Refunded'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=10, choices=PaymentMethod.choices, default=PaymentMethod.MOMO)
    status = models.CharField(max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    paystack_reference = models.CharField(max_length=100, unique=True, db_index=True)
    paystack_access_code = models.CharField(max_length=100, blank=True)
    paystack_transfer_code = models.CharField(max_length=100, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name()} - GHS {self.amount} - {self.status}"


class Payout(models.Model):

    class PayoutStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        SUCCESS = 'SUCCESS', 'Successful'
        FAILED = 'FAILED', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payouts')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payouts')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=15, choices=PayoutStatus.choices, default=PayoutStatus.PENDING)
    paystack_recipient_code = models.CharField(max_length=100, blank=True)
    paystack_transfer_code = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Payout'
        verbose_name_plural = 'Payouts'
        ordering = ['-created_at']

    def __str__(self):
        return f"Payout to {self.host.get_full_name()} - GHS {self.net_amount}"

    def save(self, *args, **kwargs):
        if not self.net_amount:
            self.platform_fee = self.amount * 0.10  # 10% platform fee
            self.net_amount = self.amount - self.platform_fee
        super().save(*args, **kwargs)