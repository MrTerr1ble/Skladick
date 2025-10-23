from django.db import models
from django.conf import settings
from decimal import Decimal


class InventoryCount(models.Model):
    """Документ инвентаризации."""
    DRAFT, IN_PROGRESS, CLOSED = "DRAFT", "IN_PROGRESS", "CLOSED"
    STATUS = [(DRAFT, "Черновик"), (IN_PROGRESS, "В работе"), (CLOSED, "Закрыт")]

    number = models.CharField("Номер", max_length=32, unique=True)
    warehouse = models.ForeignKey("warehouses.Warehouse", on_delete=models.PROTECT, verbose_name="Склад")
    status = models.CharField("Статус", max_length=16, choices=STATUS, default=DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, verbose_name="Создал")

    class Meta:
        verbose_name = "Инвентаризация"
        verbose_name_plural = "Инвентаризации"
        ordering = ["-created_at"]

    def __str__(self):
        return f"ИНВ {self.number} ({self.get_status_display()})"


class InventoryCountLine(models.Model):
    """Строка документа инвентаризации."""
    count = models.ForeignKey(InventoryCount, on_delete=models.CASCADE, related_name="lines", verbose_name="Инвентаризация")
    location = models.ForeignKey("warehouses.Location", on_delete=models.PROTECT, verbose_name="Локация")
    item = models.ForeignKey("catalog.Item", on_delete=models.PROTECT, verbose_name="Номенклатура")
    qty_book = models.DecimalField("По учёту", max_digits=18, decimal_places=3, default=Decimal("0.000"))
    qty_fact = models.DecimalField("Факт", max_digits=18, decimal_places=3, default=Decimal("0.000"))
    delta = models.DecimalField("Разница", max_digits=18, decimal_places=3, default=Decimal("0.000"))
    note = models.CharField("Примечание", max_length=255, blank=True)

    class Meta:
        verbose_name = "Строка инвентаризации"
        verbose_name_plural = "Строки инвентаризации"
        unique_together = ("count", "location", "item")
        indexes = [models.Index(fields=["count", "location", "item"])]

    def __str__(self):
        return f"{self.count.number} | {self.location} | {self.item}"
