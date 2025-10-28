from apps.catalog.models import Item

from .models import Alert, Threshold


def evaluate_thresholds(inv):
    """Проверяет инвентарь на выход за пороги и создаёт Alert."""
    if inv.item.kind == Item.ORE:
        return

    qs = Threshold.objects.filter(is_active=True, item=inv.item, warehouse=inv.location.warehouse)

    # приоритет у порога для конкретной локации
    candidates = qs.filter(location=inv.location)
    if not candidates.exists():
        candidates = qs.filter(location__isnull=True)

    for t in candidates:
        q = inv.qty_on_hand
        under = t.min_qty is not None and q < t.min_qty
        over = t.max_qty is not None and q > t.max_qty

        if not (under or over):
            continue

        severity = Alert.CRIT if under else Alert.WARN
        message = (
            "Остаток {qty} вне порога [{min} … {max}]".format(
                qty=q,
                min=t.min_qty if t.min_qty is not None else "—",
                max=t.max_qty if t.max_qty is not None else "—",
            )
        )

        open_alert = (
            Alert.objects.filter(threshold=t, state=Alert.OPEN)
            .order_by("-created_at")
            .first()
        )

        if open_alert:
            fields = {"current_qty": q, "message": message, "severity": severity}
            for field, value in fields.items():
                setattr(open_alert, field, value)
            open_alert.save(update_fields=list(fields.keys()))
            continue

        Alert.objects.create(
            state=Alert.OPEN,
            severity=severity,
            warehouse=inv.location.warehouse,
            location=inv.location,
            item=inv.item,
            current_qty=q,
            uom=inv.uom,
            threshold=t,
            message=message,
        )
