from django.db import models


class Threshold(models.Model):
    """Пороговые значения по позиции/локации (нижний/верхний)."""
    warehouse = models.ForeignKey("warehouses.Warehouse", on_delete=models.CASCADE, verbose_name="Склад")
    location = models.ForeignKey("warehouses.Location", null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Локация")
    item = models.ForeignKey("catalog.Item", on_delete=models.CASCADE, verbose_name="Номенклатура")
    min_qty = models.DecimalField("Мин. кол-во", max_digits=18, decimal_places=3, null=True, blank=True)
    max_qty = models.DecimalField("Макс. кол-во", max_digits=18, decimal_places=3, null=True, blank=True)
    uom = models.ForeignKey("catalog.Uom", on_delete=models.PROTECT, verbose_name="ЕИ")
    is_active = models.BooleanField("Активен", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Порог"
        verbose_name_plural = "Пороги"
        unique_together = ("warehouse", "location", "item")
        indexes = [models.Index(fields=["warehouse", "location", "item"])]

    def __str__(self):
        loc = self.location.code if self.location_id else "—"
        return f"{self.warehouse}/{loc}/{self.item}"


class Alert(models.Model):
    """Алерты по порогам (ниже/выше), с подтверждением и закрытием."""
    OPEN, ACK, CLOSED = "OPEN", "ACK", "CLOSED"
    STATE_CHOICES = [(OPEN, "Открыт"), (ACK, "Принят"), (CLOSED, "Закрыт")]
    INFO, WARN, CRIT = "INFO", "WARN", "CRIT"
    SEVERITY_CHOICES = [(INFO, "Инфо"), (WARN, "Внимание"), (CRIT, "Критично")]

    warehouse = models.ForeignKey("warehouses.Warehouse", on_delete=models.PROTECT, verbose_name="Склад")
    location = models.ForeignKey("warehouses.Location", null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Локация")
    item = models.ForeignKey("catalog.Item", on_delete=models.PROTECT, verbose_name="Номенклатура")
    threshold = models.ForeignKey(Threshold, null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Порог")
    current_qty = models.DecimalField("Текущее кол-во", max_digits=18, decimal_places=3)
    uom = models.ForeignKey("catalog.Uom", on_delete=models.PROTECT, verbose_name="ЕИ")
    severity = models.CharField("Важность", max_length=8, choices=SEVERITY_CHOICES, default=WARN)
    state = models.CharField("Статус", max_length=8, choices=STATE_CHOICES, default=OPEN, db_index=True)
    message = models.TextField("Сообщение", blank=True)
    correlation_id = models.CharField("Корреляция", max_length=64, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Алерт"
        verbose_name_plural = "Алерты"
        indexes = [
            models.Index(fields=["state", "created_at"]),
            models.Index(fields=["warehouse", "location", "item"]),
            models.Index(fields=["correlation_id"]),
        ]

    def __str__(self):
        return f"[{self.state}] {self.item} @ {self.warehouse}"
