from django.conf import settings
from django.db import models


class Stockpile(models.Model):
    warehouse = models.ForeignKey("warehouses.Warehouse", on_delete=models.PROTECT)
    location = models.OneToOneField("warehouses.Location", on_delete=models.PROTECT)
    code = models.CharField(max_length=50)
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Стокпайл"
        verbose_name_plural = "Стокпайлы"
        unique_together = ("warehouse", "code")
        ordering = ["warehouse__name", "code"]

    def __str__(self):
        return f"{self.code} ({self.warehouse})"


class StockpileInventory(models.Model):
    stockpile = models.ForeignKey(Stockpile, on_delete=models.PROTECT)
    item = models.ForeignKey(
        "catalog.Item",
        on_delete=models.PROTECT,
        limit_choices_to={"kind": "ORE"},
    )
    uom = models.ForeignKey("catalog.Uom", on_delete=models.PROTECT)
    qty_on_ground = models.DecimalField(max_digits=14, decimal_places=3, default=0)

    class Meta:
        verbose_name = "Остаток стокпайла"
        verbose_name_plural = "Остатки стокпайлов"
        unique_together = ("stockpile", "item")

    def __str__(self):
        return f"{self.stockpile} — {self.item}: {self.qty_on_ground} {self.uom}"


class StockpileMovement(models.Model):
    RECEIPT, ISSUE, TRANSFER = "RECEIPT", "ISSUE", "TRANSFER"
    MOVEMENT_CHOICES = [
        (RECEIPT, "Приход"),
        (ISSUE, "Расход"),
        (TRANSFER, "Перемещение"),
    ]

    movement_type = models.CharField(max_length=16, choices=MOVEMENT_CHOICES)
    item = models.ForeignKey(
        "catalog.Item",
        on_delete=models.PROTECT,
        limit_choices_to={"kind": "ORE"},
    )
    from_stockpile = models.ForeignKey(
        Stockpile,
        null=True,
        blank=True,
        related_name="movements_out",
        on_delete=models.PROTECT,
    )
    to_stockpile = models.ForeignKey(
        Stockpile,
        null=True,
        blank=True,
        related_name="movements_in",
        on_delete=models.PROTECT,
    )
    qty = models.DecimalField(max_digits=14, decimal_places=3)
    uom = models.ForeignKey("catalog.Uom", on_delete=models.PROTECT)
    occurred_at = models.DateTimeField(auto_now_add=True)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    note = models.TextField(blank=True)

    class Meta:
        verbose_name = "Движение стокпайла"
        verbose_name_plural = "Движения стокпайлов"
        ordering = ["-occurred_at"]

    def __str__(self):
        return f"{self.get_movement_type_display()} {self.qty} {self.uom} {self.item}"


class StockpileThreshold(models.Model):
    stockpile = models.ForeignKey(Stockpile, on_delete=models.CASCADE)
    item = models.ForeignKey(
        "catalog.Item",
        on_delete=models.PROTECT,
        limit_choices_to={"kind": "ORE"},
    )
    min_qty = models.DecimalField(max_digits=14, decimal_places=3, null=True, blank=True)
    max_qty = models.DecimalField(max_digits=14, decimal_places=3, null=True, blank=True)
    uom = models.ForeignKey("catalog.Uom", on_delete=models.PROTECT)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Порог стокпайла"
        verbose_name_plural = "Пороги стокпайлов"
        unique_together = ("stockpile", "item")

    def __str__(self):
        return f"Порог {self.stockpile} / {self.item}"


class StockpileAlert(models.Model):
    OPEN, ACK, CLOSED = "OPEN", "ACK", "CLOSED"
    STATE_CHOICES = [(OPEN, "Открыт"), (ACK, "Принят"), (CLOSED, "Закрыт")]

    stockpile = models.ForeignKey(Stockpile, on_delete=models.CASCADE)
    item = models.ForeignKey(
        "catalog.Item",
        on_delete=models.PROTECT,
        limit_choices_to={"kind": "ORE"},
    )
    current_qty = models.DecimalField(max_digits=14, decimal_places=3)
    uom = models.ForeignKey("catalog.Uom", on_delete=models.PROTECT)
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default=OPEN)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Алерт стокпайла"
        verbose_name_plural = "Алерты стокпайлов"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.state}] {self.stockpile} / {self.item}"
