# seed_thresholds.py
import os
import django
import sys

# Добавляем путь к apps
current_dir = os.path.dirname(__file__)
apps_path = os.path.join(current_dir, 'apps')
sys.path.insert(0, apps_path)

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skladick.settings')
django.setup()

from decimal import Decimal
from apps.catalog.models import Item
from apps.warehouses.models import Warehouse, Location
from apps.thresholds.models import Threshold, Alert

print("🚀 Начинаем заполнение граничных значений для алертов...")

try:
    # 1. Пороги для критических материалов
    print("📊 Создаем пороги для критических материалов...")

    # Критические инструменты и материалы
    critical_items = [
        {
            'sku': 'TOOL_DRILL',
            'min_qty': Decimal('10.000'),  # Минимум 10 штук
            'max_qty': Decimal('100.000')  # Максимум 100 штук
        },
        {
            'sku': 'CHEM_REAGENT',
            'min_qty': Decimal('50.000'),  # Минимум 50 литров
            'max_qty': Decimal('500.000')  # Максимум 500 литров
        },
        {
            'sku': 'SPARE_ENGINE',
            'min_qty': Decimal('2.000'),  # Минимум 2 штуки
            'max_qty': Decimal('10.000')  # Максимум 10 штук
        }
    ]

    # Пороги для обычных материалов
    normal_items = [
        {
            'sku': 'EQUIP_EXCAVATOR',
            'min_qty': Decimal('1.000'),  # Минимум 1 штука
            'max_qty': Decimal('5.000')  # Максимум 5 штук
        }
    ]

    # Получаем все склады
    warehouses = Warehouse.objects.all()

    # Создаем пороги для критических материалов на всех складах
    for warehouse in warehouses:
        for item_data in critical_items:
            try:
                item = Item.objects.get(sku=item_data['sku'])

                threshold, created = Threshold.objects.get_or_create(
                    warehouse=warehouse,
                    item=item,
                    defaults={
                        'min_qty': item_data['min_qty'],
                        'max_qty': item_data['max_qty'],
                        'uom': item.base_uom
                    }
                )
                if created:
                    print(f'  ✅ Создан порог для {item.name} на {warehouse.name}: '
                          f'min={item_data["min_qty"]}, max={item_data["max_qty"]}')

            except Item.DoesNotExist:
                print(f'  ⚠️  Товар {item_data["sku"]} не найден')

    # 2. Пороги для руды (склады северных рудников)
    print("\n⛰️ Создаем пороги для руды...")

    ore_items = [
        {
            'sku': 'ORE_COPPER',
            'min_qty': Decimal('1000.000'),  # Минимум 1000 тонн
            'max_qty': Decimal('8000.000')  # Максимум 8000 тонн
        },
        {
            'sku': 'ORE_NICKEL',
            'min_qty': Decimal('800.000'),  # Минимум 800 тонн
            'max_qty': Decimal('6000.000')  # Максимум 6000 тонн
        },
        {
            'sku': 'ORE_IRON',
            'min_qty': Decimal('2000.000'),  # Минимум 2000 тонн
            'max_qty': Decimal('12000.000')  # Максимум 12000 тонн
        },
        {
            'sku': 'ORE_GOLD',
            'min_qty': Decimal('500.000'),  # Минимум 500 тонн
            'max_qty': Decimal('3000.000')  # Максимум 3000 тонн
        }
    ]

    # Пороги для руды только на северных рудниках
    north_warehouses = Warehouse.objects.filter(code__contains='NORTH')

    for warehouse in north_warehouses:
        for ore_data in ore_items:
            try:
                item = Item.objects.get(sku=ore_data['sku'])

                threshold, created = Threshold.objects.get_or_create(
                    warehouse=warehouse,
                    item=item,
                    defaults={
                        'min_qty': ore_data['min_qty'],
                        'max_qty': ore_data['max_qty'],
                        'uom': item.base_uom
                    }
                )
                if created:
                    print(f'  ✅ Создан порог для {item.name} на {warehouse.name}: '
                          f'min={ore_data["min_qty"]}, max={ore_data["max_qty"]}')

            except Item.DoesNotExist:
                print(f'  ⚠️  Руда {ore_data["sku"]} не найдена')

    # 3. Создаем тестовые алерты для демонстрации
    print("\n⚠️ Создаем тестовые алерты...")

    # Алерт для низкого остатка бурового инструмента
    try:
        drill_item = Item.objects.get(sku='TOOL_DRILL')
        warehouse = Warehouse.objects.first()

        # Создаем алерт о низком остатке
        alert, created = Alert.objects.get_or_create(
            warehouse=warehouse,
            item=drill_item,
            current_qty=Decimal('5.000'),  # Текущий остаток ниже минимума
            uom=drill_item.base_uom,
            severity=Alert.CRIT,
            message="Критически низкий запас бурового инструмента. Необходима срочная закупка.",
            correlation_id="LOW_STOCK_DRILL_001"
        )
        if created:
            print(f'  ✅ Создан алерт: {alert.message}')

    except Item.DoesNotExist:
        print('  ⚠️  Буровой инструмент не найден для создания алерта')

    # Алерт для переполнения медной руды
    try:
        copper_item = Item.objects.get(sku='ORE_COPPER')
        north_warehouse = north_warehouses.first()

        alert, created = Alert.objects.get_or_create(
            warehouse=north_warehouse,
            item=copper_item,
            current_qty=Decimal('8500.000'),  # Текущий остаток выше максимума
            uom=copper_item.base_uom,
            severity=Alert.WARN,
            message="Превышена максимальная вместимость для медной руды. Рассмотрите возможность отгрузки.",
            correlation_id="HIGH_STOCK_COPPER_001"
        )
        if created:
            print(f'  ✅ Создан алерт: {alert.message}')

    except Item.DoesNotExist:
        print('  ⚠️  Медная руда не найдена для создания алерта')

    # 4. Статистика
    print(f"\n📈 Статистика:")
    print(f"   Всего порогов: {Threshold.objects.count()}")
    print(f"   Всего алертов: {Alert.objects.count()}")
    print(f"   Активных алертов: {Alert.objects.filter(state='OPEN').count()}")

    print("\n✅ Граничные значения и алерты успешно созданы!")

except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback

    traceback.print_exc()