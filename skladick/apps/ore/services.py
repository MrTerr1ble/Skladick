from apps.inventory.models import Movement


def create_receipt_movement(receipt):
    """Создаёт одноразовое Movement(RECEIPT) для приёмки."""
    Movement.objects.create(
        type=Movement.RECEIPT,
        occurred_at=receipt.created_at,
        item=receipt.item,
        qty=receipt.quantity,
        uom=receipt.item.base_uom,
        from_location=None,
        to_location=receipt.location,
        actor=receipt.created_by,
        note=f"Приёмка #{receipt.pk}, документ: {receipt.contract or '—'}",
    )
