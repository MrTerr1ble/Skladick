from .models import Threshold, Alert


def evaluate_thresholds(inv):
    """Проверяет инвентарь на выход за пороги и создаёт Alert."""
    qs = Threshold.objects.filter(is_active=True, item=inv.item, warehouse=inv.location.warehouse)

    # приоритет у порога для конкретной локации
    candidates = qs.filter(location=inv.location)
    if not candidates.exists():
        candidates = qs.filter(location__isnull=True)

    for t in candidates:
        q = inv.qty_on_hand
        under = (t.min_qty is not None and q < t.min_qty)
        over = (t.max_qty is not None and q > t.max_qty)
        if under or over:
            Alert.objects.create(
                state="OPEN",
                severity="HIGH" if under or over else "LOW",
                warehouse=inv.location.warehouse,
                location=inv.location,
                item=inv.item,
                current_qty=q,
                uom=inv.uom,
                threshold=t,
                message=f"Остаток {q} вне порога [{t.min_qty or '—'} … {t.max_qty or '—'}]",
            )
