from django.db import models
from decimal import Decimal
from django.conf import settings
from django.utils import timezone


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

    @property
    def current_qty(self):
        """Текущее количество в стокпайле."""
        balance = StockpileBalance.objects.filter(stockpile=self).first()
        return balance.qty if balance else Decimal("0.000")


class StockpileBalance(models.Model):
    """Остатки по стокпайлам."""
    stockpile = models.ForeignKey(Stockpile, on_delete=models.PROTECT, verbose_name="Сток-пайл")
    item = models.ForeignKey("catalog.Item", on_delete=models.PROTECT, verbose_name="Номенклатура")
    qty = models.DecimalField("Количество", max_digits=18, decimal_places=3, default=Decimal("0.000"))
    uom = models.ForeignKey("catalog.Uom", on_delete=models.PROTECT, verbose_name="Единица измерения")
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Остаток сток-пайла"
        verbose_name_plural = "Остатки сток-пайлов"
        unique_together = ("stockpile", "item")
        ordering = ["stockpile__warehouse__name", "stockpile__code"]

    def __str__(self):
        return f"{self.item} ({self.stockpile}) = {self.qty} {self.uom}"


class StockpileMovement(models.Model):
    """Операции движения по стокпайлам."""
    RECEIPT, ISSUE, TRANSFER = "RECEIPT", "ISSUE", "TRANSFER"
    TYPES = [
        (RECEIPT, "Приёмка"),
        (ISSUE, "Списание"),
        (TRANSFER, "Перемещение"),
    ]

    type = models.CharField("Тип операции", max_length=16, choices=TYPES)
    occurred_at = models.DateTimeField("Дата и время", default=timezone.now, editable=True)
    stockpile = models.ForeignKey(Stockpile, on_delete=models.PROTECT, verbose_name="Сток-пайл")
    item = models.ForeignKey("catalog.Item", on_delete=models.PROTECT, verbose_name="Номенклатура")
    qty = models.DecimalField("Количество", max_digits=18, decimal_places=3)
    uom = models.ForeignKey("catalog.Uom", on_delete=models.PROTECT, verbose_name="ЕИ")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL, verbose_name="Оператор")
    note = models.TextField("Комментарий", blank=True)

    # Для перемещений между стокпайлами
    from_stockpile = models.ForeignKey(
        Stockpile, null=True, blank=True,
        related_name="outgoing_transfers", on_delete=models.PROTECT, verbose_name="Из сток-пайла"
    )
    to_stockpile = models.ForeignKey(
        Stockpile, null=True, blank=True,
        related_name="incoming_transfers", on_delete=models.PROTECT, verbose_name="В сток-пайл"
    )

    class Meta:
        verbose_name = "Движение сток-пайла"
        verbose_name_plural = "Движения сток-пайлов"
        ordering = ["-occurred_at"]

    def __str__(self):
        return f"{self.get_type_display()} {self.qty} {self.uom} {self.item} ({self.stockpile})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Обновляем баланс стокпайла
        self._update_balance()

    def _update_balance(self):
        """Обновляет баланс стокпайла после движения."""
        balance, created = StockpileBalance.objects.get_or_create(
            stockpile=self.stockpile,
            item=self.item,
            defaults={'qty': Decimal('0.000'), 'uom': self.uom}
        )

        if self.type == self.RECEIPT:
            balance.qty += self.qty
        elif self.type == self.ISSUE:
            balance.qty -= self.qty
        elif self.type == self.TRANSFER:
            if self.from_stockpile == self.stockpile:
                balance.qty -= self.qty
            elif self.to_stockpile == self.stockpile:
                balance.qty += self.qty

        balance.save()


class StockpileThreshold(models.Model):
    """Пороговые значения для стокпайлов."""
    stockpile = models.OneToOneField(
        Stockpile, on_delete=models.CASCADE,
        related_name="threshold", verbose_name="Сток-пайл"
    )
    min_qty = models.DecimalField("Мин. кол-во", max_digits=18, decimal_places=3, null=True, blank=True)
    max_qty = models.DecimalField("Макс. кол-во", max_digits=18, decimal_places=3, null=True, blank=True)
    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Порог сток-пайла"
        verbose_name_plural = "Пороги сток-пайлов"

    def check_thresholds(self, current_qty):
        """Проверяет, выходит ли текущее количество за пороги."""
        alerts = []
        if self.min_qty is not None and current_qty <= self.min_qty:
            alerts.append(("CRIT", f"Количество ниже минимального: {current_qty} <= {self.min_qty}"))
        elif self.max_qty is not None and current_qty >= self.max_qty:
            alerts.append(("WARN", f"Количество превышает максимальное: {current_qty} >= {self.max_qty}"))
        return alerts


class StockpileAlert(models.Model):
    """Алерты для стокпайлов."""
    OPEN, ACK, CLOSED = "OPEN", "ACK", "CLOSED"
    WARN, CRIT = "WARN", "CRIT"

    stockpile = models.ForeignKey(Stockpile, on_delete=models.CASCADE, verbose_name="Сток-пайл")
    current_qty = models.DecimalField("Текущее кол-во", max_digits=18, decimal_places=3)
    severity = models.CharField("Важность", max_length=8, choices=[(WARN, "Внимание"), (CRIT, "Критично")],
                                default=WARN)
    state = models.CharField("Статус", max_length=8, choices=[(OPEN, "Открыт"), (ACK, "Принят"), (CLOSED, "Закрыт")],
                             default=OPEN)
    message = models.TextField("Сообщение", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name="Кем принято"
    )
    acknowledged_at = models.DateTimeField("Когда принято", null=True, blank=True)

    class Meta:
        verbose_name = "Алерт сток-пайла"
        verbose_name_plural = "Алерты сток-пайлов"
        ordering = ["-created_at"]

    def acknowledge(self, user):
        """Отметить алерт как принятый."""
        self.state = self.ACK
        self.acknowledged_by = user
        self.acknowledged_at = timezone.now()
        self.save()