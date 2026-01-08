from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Wallet


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_wallet(sender, instance, created, **kwargs):
    """Create a wallet automatically when a new user is created"""
    if created:
        Wallet.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_wallet(sender, instance, **kwargs):
    """Save wallet when user is saved"""
    if hasattr(instance, 'wallet'):
        instance.wallet.save()
