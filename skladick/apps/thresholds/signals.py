from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Alert


@receiver(post_save, sender=Alert)
def notify_new_alert(sender, instance: Alert, created, **kwargs):
    if not created or instance.state != "OPEN":
        return

    channel_layer = get_channel_layer()
    data = {
        "type": "send_alert",
        "data": {
            "id": instance.id,
            "item": instance.item.name,
            "qty": float(instance.current_qty),
            "uom": instance.uom.code,
            "warehouse": instance.warehouse.name,
            "location": instance.location.code if instance.location else "-",
            "message": instance.message,
        },
    }
    async_to_sync(channel_layer.group_send)("alert_updates", data)
