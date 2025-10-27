from django.db import models
from django.conf import settings


class OreReceipt(models.Model):
    """Регистрация приёмки руды."""
    location = models.ForeignKey("warehouses.Location", on_delete=models.PROTECT, verbose_name="Локация приёмки")
    item = models.ForeignKey("catalog.Item", on_delete=models.PROTECT, verbose_name="Тип руды")
    quantity = models.DecimalField("Количество", max_digits=12, decimal_places=3)
    contract = models.FileField("Документ (накладная/контракт)", upload_to="contracts/", blank=True, null=True)
    created_at = models.DateTimeField("Дата приёмки", auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, verbose_name="Оператор")
    note = models.TextField(blank=True)
    file = models.FileField(upload_to="ore_docs/", null=True, blank=True)

    class Meta:
        verbose_name = "Приёмка руды"
        verbose_name_plural = "Приёмки руды"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Приёмка {self.item} ({self.quantity}) в {self.location}"
