from django.core.management.base import BaseCommand
from apps.inventory.models import Inventory
from apps.thresholds.models import Threshold, Alert
from decimal import Decimal


class Command(BaseCommand):
    help = 'Проверяет все остатки на соответствие порогам и создает алерты'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Проверяем остатки на соответствие порогам...')

        checked = 0
        alerts_created = 0

        for inventory in Inventory.objects.all():
            checked += 1
            new_alerts = self.check_inventory_thresholds(inventory)
            alerts_created += new_alerts

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Проверено {checked} остатков, создано {alerts_created} алертов'
            )
        )

    def check_inventory_thresholds(self, inventory):
        """Проверяет один остаток на соответствие порогам"""
        alerts_created = 0

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
                alert, created = Alert.objects.get_or_create(
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
                if created:
                    alerts_created += 1
                    self.stdout.write(f'  ⚠️  Создан алерт: {alert.message}')

            # Проверяем максимальный порог
            elif threshold.max_qty is not None and current_qty >= threshold.max_qty:
                alert, created = Alert.objects.get_or_create(
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
                if created:
                    alerts_created += 1
                    self.stdout.write(f'  ⚠️  Создан алерт: {alert.message}')

        return alerts_created