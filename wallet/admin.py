from django.contrib import admin
from .models import Wallet, Card, Transaction, QRCode


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'currency', 'created_at', 'updated_at')
    list_filter = ('currency', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('card_holder_name', 'card_type', 'bank_name', 'card_number', 'is_primary', 'user', 'created_at')
    list_filter = ('card_type', 'is_primary', 'bank_name', 'created_at')
    search_fields = ('card_holder_name', 'card_number', 'user__email', 'bank_name')
    readonly_fields = ('created_at',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'user', 'transaction_type', 'amount', 'status', 'created_at')
    list_filter = ('transaction_type', 'status', 'created_at', 'category')
    search_fields = ('transaction_id', 'user__email', 'description', 'recipient_email', 'sender_email')
    readonly_fields = ('transaction_id', 'created_at')


@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'qr_code', 'amount', 'is_active', 'expires_at', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__email', 'qr_code', 'description')
    readonly_fields = ('created_at',)
