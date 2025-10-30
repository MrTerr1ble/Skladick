from django.db import models
from decimal import Decimal
from django.conf import settings
from django.utils import timezone


class Inventory(models.Model):
    """Остатки по товарам и локациям (обычные склады)."""
    location = models.ForeignKey("warehouses.Location", on_delete=models.PROTECT, verbose_name="Локация")
    item = models.ForeignKey("catalog.Item", on_delete=models.PROTECT, verbose_name="Номенклатура")
    qty_on_hand = models.DecimalField("Количество", max_digits=18, decimal_places=3, default=Decimal("0.000"))
    uom = models.ForeignKey("catalog.Uom", on_delete=models.PROTECT, verbose_name="Единица измерения")

    class Meta:
        verbose_name = "Остаток"
        verbose_name_plural = "Остатки"
        unique_together = ("location", "item")
        ordering = ["location__warehouse__name", "location__code"]

    def __str__(self):
        return f"{self.item} ({self.location}) = {self.qty_on_hand} {self.uom}"


class Movement(models.Model):
    """Операции движения (приёмка, списание, перемещение) для обычных складов."""
    RECEIPT, ISSUE, TRANSFER = "RECEIPT", "ISSUE", "TRANSFER"
    TYPES = [
        (RECEIPT, "Приёмка"),
        (ISSUE, "Списание"),
        (TRANSFER, "Перемещение"),
    ]

    type = models.CharField("Тип операции", max_length=16, choices=TYPES)
    occurred_at = models.DateTimeField(verbose_name="Дата и время", default=timezone.now, editable=True,)
    item = models.ForeignKey("catalog.Item", on_delete=models.PROTECT, verbose_name="Номенклатура")
    from_location = models.ForeignKey(
        "warehouses.Location", null=True, blank=True,
        related_name="+", on_delete=models.PROTECT, verbose_name="Откуда"
    )
    to_location = models.ForeignKey(
        "warehouses.Location", null=True, blank=True,
        related_name="+", on_delete=models.PROTECT, verbose_name="Куда"
    )
    qty = models.DecimalField("Количество", max_digits=18, decimal_places=3)
    uom = models.ForeignKey("catalog.Uom", on_delete=models.PROTECT, verbose_name="ЕИ")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, verbose_name="Оператор")
    note = models.TextField("Комментарий", blank=True)

    class Meta:
        verbose_name = "Движение"
        verbose_name_plural = "Движения"
        ordering = ["-occurred_at"]

    def __str__(self):
        return f"{self.get_type_display()} {self.qty} {self.uom} {self.item}"