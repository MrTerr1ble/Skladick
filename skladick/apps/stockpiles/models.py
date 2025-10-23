from django.db import models


class Stockpile(models.Model):
    """Сток-пайл (куча/резервуар) для руды/сыпучих материалов."""
    warehouse = models.ForeignKey("warehouses.Warehouse", on_delete=models.CASCADE, verbose_name="Склад")
    code = models.CharField("Код", max_length=32)
    name = models.CharField("Название", max_length=128)
    capacity_qty = models.DecimalField("Вместимость", max_digits=18, decimal_places=3, null=True, blank=True)
    uom = models.ForeignKey("catalog.Uom", on_delete=models.PROTECT, verbose_name="ЕИ")

    class Meta:
        verbose_name = "Сток-пайл"
        verbose_name_plural = "Сток-пайлы"
        unique_together = ("warehouse", "code")
        ordering = ["warehouse__name", "code"]

    def __str__(self):
        return f"{self.warehouse}:{self.code}"


class StockpileThreshold(models.Model):
    stockpile = models.OneToOneField(Stockpile, on_delete=models.CASCADE, related_name="threshold", verbose_name="Сток-пайл")
    min_qty = models.DecimalField("Мин. кол-во", max_digits=18, decimal_places=3, null=True, blank=True)
    max_qty = models.DecimalField("Макс. кол-во", max_digits=18, decimal_places=3, null=True, blank=True)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Порог сток-пайла"
        verbose_name_plural = "Пороги сток-пайлов"


class StockpileAlert(models.Model):
    OPEN, ACK, CLOSED = "OPEN", "ACK", "CLOSED"
    WARN, CRIT = "WARN", "CRIT"

    stockpile = models.ForeignKey(Stockpile, on_delete=models.CASCADE, verbose_name="Сток-пайл")
    current_qty = models.DecimalField("Текущее кол-во", max_digits=18, decimal_places=3)
    severity = models.CharField("Важность", max_length=8, choices=[(WARN, "Внимание"), (CRIT, "Критично")], default=WARN)
    state = models.CharField("Статус", max_length=8, choices=[(OPEN, "Открыт"), (ACK, "Принят"), (CLOSED, "Закрыт")], default=OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Алерт сток-пайла"
        verbose_name_plural = "Алерты сток-пайлов"
        ordering = ["-created_at"]
