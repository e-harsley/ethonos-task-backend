from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class Wallet(models.Model):
    """User's wallet to hold balance and manage transactions"""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, default='NGN')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'wallets'

    def __str__(self):
        return f"{self.user.email}'s Wallet - {self.currency} {self.balance}"


class Card(models.Model):
    """Linked bank account/credit/debit cards"""
    CARD_TYPES = [
        ('credit', 'Credit Card'),
        ('debit', 'Debit Card'),
        ('bank', 'Bank Account'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cards')
    card_number = models.CharField(max_length=19)
    card_type = models.CharField(max_length=10, choices=CARD_TYPES)
    card_holder_name = models.CharField(max_length=200)
    expiry_date = models.CharField(max_length=7, blank=True, null=True)
    bank_name = models.CharField(max_length=100)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'cards'
        ordering = ['-is_primary', '-created_at']

    def __str__(self):
        return f"{self.card_holder_name} - {self.card_number[-4:]}"

    def save(self, *args, **kwargs):
        # If this card is set as primary, unset all other primary cards for this user
        if self.is_primary:
            Card.objects.filter(user=self.user, is_primary=True).update(is_primary=False)
        super().save(*args, **kwargs)


class Transaction(models.Model):
    """Transaction records for income and expenses"""
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('transfer_in', 'Transfer In'),
        ('transfer_out', 'Transfer Out'),
    ]

    TRANSACTION_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    transaction_type = models.CharField(max_length=15, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    description = models.CharField(max_length=255)
    category = models.CharField(max_length=50, blank=True, null=True)
    status = models.CharField(max_length=15, choices=TRANSACTION_STATUS, default='completed')
    recipient_email = models.EmailField(blank=True, null=True)
    sender_email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} - {self.user.email}"


class QRCode(models.Model):
    """QR codes for receiving money"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='qr_codes')
    qr_code = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'qr_codes'
        ordering = ['-created_at']

    def __str__(self):
        return f"QR Code for {self.user.email}"

    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
