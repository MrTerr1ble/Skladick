# seed_data.py
import os
import django
import sys
from decimal import Decimal
import random
from django.utils import timezone

# Добавляем путь к apps
current_dir = os.path.dirname(__file__)
apps_path = os.path.join(current_dir, 'apps')
sys.path.insert(0, apps_path)

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skladick.settings')
django.setup()

print("🚀 Начинаем заполнение базы данных...")

try:
    # 1. Склады и локации
    print("📦 Создаем склады и локации...")
    from apps.warehouses.models import Warehouse, Location

    warehouses_data = [
        {'code': 'WH_NORTH_1', 'name': 'Северный рудник №1'},
        {'code': 'WH_NORTH_2', 'name': 'Северный рудник №2'},
        {'code': 'WH_CENTRAL_1', 'name': 'Перерабатывающий завод №1'},
        {'code': 'WH_CENTRAL_2', 'name': 'Перерабатывающий завод №2'},
    ]

    for data in warehouses_data:
        wh, created = Warehouse.objects.get_or_create(**data)
        if created:
            print(f'  ✅ Создан склад: {wh.name}')

    # Создаем локации для каждого склада
    locations_data = [
        {'code': 'ZONE_A', 'name': 'Зона А - Основное хранение'},
        {'code': 'ZONE_B', 'name': 'Зона Б - Буферная'},
        {'code': 'ZONE_C', 'name': 'Зона В - Карантин'},
        {'code': 'YARD_1', 'name': 'Открытая площадка 1'},
    ]

    for warehouse in Warehouse.objects.all():
        for loc_data in locations_data:
            loc, created = Location.objects.get_or_create(
                warehouse=warehouse,
                code=f"{warehouse.code}_{loc_data['code']}",
                name=f"{warehouse.name} - {loc_data['name']}"
            )
            if created:
                print(f'  ✅ Создана локация: {loc.name}')

    # 2. Единицы измерения и номенклатура
    print("📋 Создаем единицы измерения и номенклатуру...")
    from apps.catalog.models import Uom, Item, Supplier

    # Единицы измерения
    uoms_data = [
        {'code': 'TON', 'name': 'Тонна'},
        {'code': 'KG', 'name': 'Килограмм'},
        {'code': 'PCS', 'name': 'Штука'},
        {'code': 'L', 'name': 'Литр'},
        {'code': 'M3', 'name': 'Кубический метр'},
    ]

    for data in uoms_data:
        uom, created = Uom.objects.get_or_create(**data)
        if created:
            print(f'  ✅ Создана единица измерения: {uom.name}')

    # Поставщики
    suppliers_data = [
        {'code': 'SUP_001', 'name': 'ООО Горные технологии'},
        {'code': 'SUP_002', 'name': 'ЗАО Промышленные решения'},
        {'code': 'SUP_003', 'name': 'АО Металлсервис'},
    ]

    for data in suppliers_data:
        supplier, created = Supplier.objects.get_or_create(**data)
        if created:
            print(f'  ✅ Создан поставщик: {supplier.name}')

    # Номенклатура - БЕЗ tracking_mode
    items_data = [
        {'sku': 'ORE_COPPER', 'name': 'Медная руда', 'base_uom_id': 1},
        {'sku': 'ORE_NICKEL', 'name': 'Никелевая руда', 'base_uom_id': 1},
        {'sku': 'ORE_IRON', 'name': 'Железная руда', 'base_uom_id': 1},
        {'sku': 'ORE_GOLD', 'name': 'Золотосодержащая руда', 'base_uom_id': 1},
        {'sku': 'TOOL_DRILL', 'name': 'Буровой инструмент', 'base_uom_id': 3},
        {'sku': 'EQUIP_EXCAVATOR', 'name': 'Экскаватор', 'base_uom_id': 3},
        {'sku': 'SPARE_ENGINE', 'name': 'Двигатель запасной', 'base_uom_id': 3},
        {'sku': 'CHEM_REAGENT', 'name': 'Флотационный реагент', 'base_uom_id': 4},
    ]

    for item_data in items_data:
        item, created = Item.objects.get_or_create(**item_data)
        if created:
            print(f'  ✅ Создана номенклатура: {item.name}')

    # 3. Пользователи
    print("👥 Создаем пользователей системы...")
    from apps.users.models import User

    users_data = [
        {'username': 'admin', 'password': 'admin123', 'full_name': 'Администратор Системы', 'role': 'ADMIN'},
        {'username': 'operator1', 'password': 'operator123', 'full_name': 'Иванов Иван Иванович', 'role': 'OPERATOR'},
        {'username': 'warehouse1', 'password': 'warehouse123', 'full_name': 'Петров Петр Петрович',
         'role': 'WAREHOUSE'},
        {'username': 'analyst1', 'password': 'analyst123', 'full_name': 'Сидорова Мария Сергеевна', 'role': 'ANALYST'},
    ]

    for user_data in users_data:
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults={
                'full_name': user_data['full_name'],
                'role': user_data['role'],
                'is_staff': True,
                'is_active': True
            }
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
            print(f'  ✅ Создан пользователь: {user.full_name}')

    # 4. Начальные остатки
    print("📊 Создаем начальные остатки...")
    from apps.inventory.models import Inventory, Movement

    # Создаем начальные остатки для всех товаров
    items = Item.objects.all()[:4]  # Берем первые 4 товара
    locations = Location.objects.all()[:3]  # Берем первые 3 локации

    for location in locations:
        for item in items:
            qty = Decimal(str(random.randint(10, 100)))
            inventory, created = Inventory.objects.get_or_create(
                location=location,
                item=item,
                defaults={'qty_on_hand': qty, 'uom': item.base_uom}
            )

            if created:
                Movement.objects.create(
                    type=Movement.RECEIPT,
                    occurred_at=timezone.now(),
                    item=item,
                    to_location=location,
                    qty=qty,
                    uom=item.base_uom,
                    note="Начальный остаток"
                )
                print(f'  ✅ Создан остаток: {item.name} в {location.name} - {qty}')

    # 5. Сток-пайлы для руды
    print("⛰️ Создаем сток-пайлы для руды...")
    try:
        from stockpiles.models import Stockpile, StockpileThreshold

        # Получаем тонны
        ton_uom = Uom.objects.get(code='TON')

        # Создаем сток-пайлы для северных рудников
        stockpiles_data = [
            {'code': 'SP_COPPER_1', 'name': 'Медная руда - Основная куча', 'capacity_qty': Decimal('10000.000')},
            {'code': 'SP_NICKEL_1', 'name': 'Никелевая руда - Основная куча', 'capacity_qty': Decimal('8000.000')},
            {'code': 'SP_IRON_1', 'name': 'Железная руда - Основная куча', 'capacity_qty': Decimal('15000.000')},
        ]

        for warehouse in Warehouse.objects.filter(code__contains='NORTH'):
            for sp_data in stockpiles_data:
                stockpile, created = Stockpile.objects.get_or_create(
                    warehouse=warehouse,
                    code=f"{warehouse.code}_{sp_data['code']}",
                    defaults={
                        'name': f"{warehouse.name} - {sp_data['name']}",
                        'capacity_qty': sp_data['capacity_qty'],
                        'uom': ton_uom
                    }
                )

                if created:
                    print(f'  ✅ Создан сток-пайл: {stockpile.name}')

    except ImportError:
        print('  ⚠️  Модуль stockpiles не найден, пропускаем...')

    # 6. Заявки на закупку
    print("📝 Создаем заявки на закупку...")
    try:
        from procurement.models import PurchaseRequest

        # Создаем тестовую заявку
        low_stock_item = Item.objects.get(sku='TOOL_DRILL')
        supplier = Supplier.objects.first()
        warehouse = Warehouse.objects.first()

        pr, created = PurchaseRequest.objects.create(
            item=low_stock_item,
            qty=Decimal('50.000'),
            uom=low_stock_item.base_uom,
            warehouse=warehouse,
            supplier=supplier,
            state=PurchaseRequest.SUBMITTED,
            comment="Срочная закупка в связи с низкими остатками"
        )
        if created:
            print(f'  ✅ Создана заявка на закупку: {pr.item.name}')

    except ImportError:
        print('  ⚠️  Модуль procurement не найден, пропускаем...')

    # 7. Транспорт
    print("🚚 Создаем транспортные единицы...")
    try:
        from transport.models import TransportUnit

        transport_data = [
            {'type': 'TRUCK', 'number': 'А123БВ77'},
            {'type': 'TRUCK', 'number': 'В456ГД78'},
            {'type': 'TRAIN', 'number': '745632'},
            {'type': 'TRAIN', 'number': '845213'},
        ]

        for data in transport_data:
            unit, created = TransportUnit.objects.get_or_create(**data)
            if created:
                print(f'  ✅ Создана транспортная единица: {unit}')

    except ImportError:
        print('  ⚠️  Модуль transport не найден, пропускаем...')

    print("✅ База данных успешно заполнена тестовыми данными!")


    def create_thresholds_and_alerts(self):
        self.stdout.write("⚠️ Создаем граничные значения и алерты...")

        try:
            from thresholds.models import Threshold, Alert
            from catalog.models import Item
            from warehouses.models import Warehouse

            # Критические материалы
            critical_items = [
                {'sku': 'TOOL_DRILL', 'min_qty': Decimal('10.000'), 'max_qty': Decimal('100.000')},
                {'sku': 'CHEM_REAGENT', 'min_qty': Decimal('50.000'), 'max_qty': Decimal('500.000')},
                {'sku': 'SPARE_ENGINE', 'min_qty': Decimal('2.000'), 'max_qty': Decimal('10.000')},
            ]

            # Пороги для руды
            ore_items = [
                {'sku': 'ORE_COPPER', 'min_qty': Decimal('1000.000'), 'max_qty': Decimal('8000.000')},
                {'sku': 'ORE_NICKEL', 'min_qty': Decimal('800.000'), 'max_qty': Decimal('6000.000')},
                {'sku': 'ORE_IRON', 'min_qty': Decimal('2000.000'), 'max_qty': Decimal('12000.000')},
                {'sku': 'ORE_GOLD', 'min_qty': Decimal('500.000'), 'max_qty': Decimal('3000.000')},
            ]

            # Создаем пороги для всех складов
            for warehouse in Warehouse.objects.all():
                # Критические материалы на всех складах
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
                            self.stdout.write(f'  ✅ Порог: {item.name} на {warehouse.name}')
                    except Item.DoesNotExist:
                        pass

                # Руда только на северных складах
                if 'NORTH' in warehouse.code:
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
                                self.stdout.write(f'  ✅ Порог руды: {item.name} на {warehouse.name}')
                        except Item.DoesNotExist:
                            pass

            # Тестовые алерты
            try:
                drill_item = Item.objects.get(sku='TOOL_DRILL')
                warehouse = Warehouse.objects.first()

                Alert.objects.get_or_create(
                    warehouse=warehouse,
                    item=drill_item,
                    current_qty=Decimal('5.000'),
                    uom=drill_item.base_uom,
                    severity=Alert.CRIT,
                    message="Критически низкий запас бурового инструмента",
                    correlation_id="DEMO_ALERT_001"
                )
                self.stdout.write('  ✅ Демо-алерт создан')

            except Item.DoesNotExist:
                pass

        except ImportError as e:
            self.stdout.write(f'  ❌ Ошибка импорта thresholds: {e}')

except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback

    traceback.print_exc()