from django.db import models
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import F


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
        constraints = [
            models.CheckConstraint(
                check=models.Q(qty_on_hand__gte=0),
                name='non_negative_qty'
            )
        ]

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
    occurred_at = models.DateTimeField(verbose_name="Дата и время", default=timezone.now, editable=True, )
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

    def clean(self):
        """Валидация перед сохранением"""
        # Проверка для списания
        if self.type == self.ISSUE:
            if self.from_location:
                try:
                    inventory = Inventory.objects.get(
                        location=self.from_location,
                        item=self.item
                    )
                    if inventory.qty_on_hand < self.qty:
                        raise ValidationError(
                            f"Недостаточно остатков для списания. "
                            f"Доступно: {inventory.qty_on_hand}, требуется: {self.qty}"
                        )
                except Inventory.DoesNotExist:
                    raise ValidationError("Нет остатков для списания в указанной локации")

        # Проверка для перемещения
        elif self.type == self.TRANSFER:
            if not self.from_location or not self.to_location:
                raise ValidationError("Для перемещения должны быть указаны 'Откуда' и 'Куда'")

            if self.from_location == self.to_location:
                raise ValidationError("Нельзя перемещать в ту же локацию")

            # Проверяем остатки в исходной локации
            try:
                from_inventory = Inventory.objects.get(
                    location=self.from_location,
                    item=self.item
                )
                if from_inventory.qty_on_hand < self.qty:
                    raise ValidationError(
                        f"Недостаточно остатков для перемещения. "
                        f"Доступно в {self.from_location}: {from_inventory.qty_on_hand}, "
                        f"требуется: {self.qty}"
                    )
            except Inventory.DoesNotExist:
                raise ValidationError(f"Нет остатков для перемещения в локации {self.from_location}")

    def save(self, *args, **kwargs):
        # Вызываем валидацию
        self.full_clean()
        super().save(*args, **kwargs)

        # Обновляем остатки
        self.update_inventory()

    def update_inventory(self):
        """Обновляет остатки после движения и создает алерты"""
        if self.type == self.RECEIPT and self.to_location:
            # При приёмке увеличиваем остатки
            inventory, created = Inventory.objects.get_or_create(
                location=self.to_location,
                item=self.item,
                defaults={'qty_on_hand': self.qty, 'uom': self.uom}
            )
            if not created:
                inventory.qty_on_hand = F('qty_on_hand') + self.qty
                inventory.save()

            # Проверяем пороги и создаем алерты
            self.check_thresholds_and_create_alerts(inventory)

        elif self.type == self.ISSUE and self.from_location:
            # При списании уменьшаем остатки
            inventory = Inventory.objects.get(
                location=self.from_location,
                item=self.item
            )
            inventory.qty_on_hand = F('qty_on_hand') - self.qty
            inventory.save()

            # Проверяем пороги и создаем алерты
            self.check_thresholds_and_create_alerts(inventory)

        elif self.type == self.TRANSFER:
            # При перемещении уменьшаем в исходной и увеличиваем в целевой
            # Уменьшаем в from_location
            from_inventory = Inventory.objects.get(
                location=self.from_location,
                item=self.item
            )
            from_inventory.qty_on_hand = F('qty_on_hand') - self.qty
            from_inventory.save()

            # Проверяем пороги для исходной локации
            self.check_thresholds_and_create_alerts(from_inventory)

            # Увеличиваем в to_location
            to_inventory, created = Inventory.objects.get_or_create(
                location=self.to_location,
                item=self.item,
                defaults={'qty_on_hand': self.qty, 'uom': self.uom}
            )
            if not created:
                to_inventory.qty_on_hand = F('qty_on_hand') + self.qty
                to_inventory.save()

            # Проверяем пороги для целевой локации
            self.check_thresholds_and_create_alerts(to_inventory)

    def check_thresholds_and_create_alerts(self, inventory):
        """Проверяет пороги и создает алерты при нарушении"""
        try:
            from thresholds.models import Threshold, Alert

            # Ищем пороги для этого склада и товара
            thresholds = Threshold.objects.filter(
                warehouse=inventory.location.warehouse,
                item=inventory.item,
                is_active=True
            )

            for threshold in thresholds:
                current_qty = inventory.qty_on_hand

                # Проверяем минимальный порог
                if threshold.min_qty is not None and current_qty <= threshold.min_qty:
                    Alert.objects.get_or_create(
                        warehouse=inventory.location.warehouse,
                        item=inventory.item,
                        threshold=threshold,
                        current_qty=current_qty,
                        uom=inventory.uom,
                        severity=Alert.CRIT,
                        message=f"Критически низкий запас {inventory.item.name}. "
                                f"Текущий остаток: {current_qty} {inventory.uom}, "
                                f"минимум: {threshold.min_qty} {threshold.uom}",
                        correlation_id=f"LOW_{inventory.item.sku}_{inventory.location.id}"
                    )

                # Проверяем максимальный порог
                elif threshold.max_qty is not None and current_qty >= threshold.max_qty:
                    Alert.objects.get_or_create(
                        warehouse=inventory.location.warehouse,
                        item=inventory.item,
                        threshold=threshold,
                        current_qty=current_qty,
                        uom=inventory.uom,
                        severity=Alert.WARN,
                        message=f"Превышена максимальная вместимость для {inventory.item.name}. "
                                f"Текущий остаток: {current_qty} {inventory.uom}, "
                                f"максимум: {threshold.max_qty} {threshold.uom}",
                        correlation_id=f"HIGH_{inventory.item.sku}_{inventory.location.id}"
                    )

        except ImportError:
            # Если модуль thresholds не установлен, пропускаем создание алертов
            pass

    class Meta:
        verbose_name = "Движение"
        verbose_name_plural = "Движения"
        ordering = ["-occurred_at"]

    def __str__(self):
        return f"{self.get_type_display()} {self.qty} {self.uom} {self.item}"