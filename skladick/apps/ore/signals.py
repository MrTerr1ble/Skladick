from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.catalog.models import Item
from apps.ore.models import OreReceipt
from apps.stockpiles.models import Stockpile, StockpileInventory, StockpileMovement


@receiver(post_save, sender=OreReceipt)
def on_receipt_created(sender, instance: OreReceipt, created, **kwargs):
    if not created:
        return
    if instance.item.kind != Item.ORE:
        return

    stockpile = Stockpile.objects.get(location=instance.location)
    StockpileMovement.objects.create(
        movement_type=StockpileMovement.RECEIPT,
        item=instance.item,
        to_stockpile=stockpile,
        qty=instance.quantity,
        uom=instance.item.base_uom,
        actor=instance.created_by,
        note=f"Приёмка руды #{instance.pk}",
    )
    inv, _ = StockpileInventory.objects.get_or_create(
        stockpile=stockpile,
        item=instance.item,
        defaults={"uom": instance.item.base_uom, "qty_on_ground": 0},
    )
    inv.qty_on_ground += instance.quantity
    inv.save()
