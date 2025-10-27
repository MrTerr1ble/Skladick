from django.db import models
from django.utils.crypto import get_random_string
from django.conf import settings


class PurchaseRequest(models.Model):
    """Заявка на закупку."""
    DRAFT, SUBMITTED, APPROVED, ORDERED, CLOSED, REJECTED = \
        "DRAFT", "SUBMITTED", "APPROVED", "ORDERED", "CLOSED", "REJECTED"
    STATE = [
        (DRAFT, "Черновик"),
        (SUBMITTED, "Отправлена"),
        (APPROVED, "Согласована"),
        (ORDERED, "Заказано"),
        (CLOSED, "Закрыта"),
        (REJECTED, "Отклонена"),
    ]

    number = models.CharField("Номер", max_length=50, unique=True, blank=True)
    item = models.ForeignKey("catalog.Item", on_delete=models.PROTECT, verbose_name="Номенклатура")
    qty = models.DecimalField("Кол-во", max_digits=18, decimal_places=3)
    uom = models.ForeignKey("catalog.Uom", on_delete=models.PROTECT, verbose_name="ЕИ")
    warehouse = models.ForeignKey("warehouses.Warehouse", on_delete=models.PROTECT, verbose_name="Склад")
    supplier = models.ForeignKey("catalog.Supplier", null=True, blank=True, on_delete=models.SET_NULL, verbose_name="Поставщик")
    state = models.CharField("Статус", max_length=10, choices=STATE, default=DRAFT, db_index=True)
    comment = models.TextField("Комментарий", blank=True)
    attachment = models.FileField("Приложение", upload_to="procurement/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, verbose_name="Автор")

    class Meta:
        verbose_name = "Заявка на закупку"
        verbose_name_plural = "Заявки на закупку"
        ordering = ["-created_at"]

    def __str__(self):
        return f"PR {self.number} {self.item} ({self.get_state_display()})"
    
    def save(self, *args, **kwargs):
        if not self.number:
            self.number = f"REQ-{get_random_string(6).upper()}"
        super().save(*args, **kwargs)
