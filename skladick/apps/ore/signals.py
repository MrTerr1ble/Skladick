from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import OreReceipt
from .services import create_receipt_movement


@receiver(post_save, sender=OreReceipt)
def on_receipt_created(sender, instance: OreReceipt, created, **kwargs):
    if not created:
        return
    create_receipt_movement(instance)
