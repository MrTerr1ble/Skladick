from django.db import transaction
from .models import Inventory, Movement


@transaction.atomic
def apply_movement(m: Movement):
    """Перекидывает количество между инвенторями (с блокировкой строк)."""
    def lock_inv(location):
        inv, _ = Inventory.objects.select_for_update().get_or_create(
            location=location, item=m.item,
            defaults={"uom": m.uom, "qty_on_hand": 0}
        )
        return inv

    touched = []

    if m.type in (Movement.ISSUE, Movement.TRANSFER) and m.from_location:
        inv_from = lock_inv(m.from_location)
        inv_from.qty_on_hand -= m.qty
        inv_from.save(update_fields=["qty_on_hand"])
        touched.append(inv_from)

    if m.type in (Movement.RECEIPT, Movement.TRANSFER) and m.to_location:
        inv_to = lock_inv(m.to_location)
        inv_to.qty_on_hand += m.qty
        inv_to.save(update_fields=["qty_on_hand"])
        touched.append(inv_to)

    return touched  # вернём, чтобы проверять пороги
