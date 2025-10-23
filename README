# 📦 ISUS — Складская информационная система (Django + HTML)

Полноценный учебный Django-проект на чистом HTML (без React/Vue) с серверными шаблонами (DTL).  
Реализует бизнес-логику из ТЗ: учёт складов, локаций, номенклатуры, остатков, движений, приёмку руды, а также расширения — пороги, алерты, инвентаризацию, закупки, транспорт и отчёты.

---

## 🚀 Быстрый запуск проекта

### 1️⃣ Подготовка окружения

```bash
git clone <repo-url> isus
cd isus
python -m venv .venv
# Windows:
. .venv/Scripts/activate
# macOS/Linux:
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2️⃣ requirements.txt

```txt
Django==5.2.7
psycopg2-binary==2.9.9
Pillow==10.4.0
django-debug-toolbar==4.4.6
```

### 3️⃣ Настройки (`skladick/settings.py`)

```python
AUTH_USER_MODEL = "users.User"

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth",
    "django.contrib.contenttypes", "django.contrib.sessions",
    "django.contrib.messages", "django.contrib.staticfiles",
    "apps.users", "apps.catalog", "apps.warehouses", "apps.inventory", "apps.ore",
    "apps.thresholds", "apps.stockpiles", "apps.inventory_count",
    "apps.sync", "apps.reports", "apps.procurement", "apps.transport",
]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
```

### 4️⃣ Миграции и запуск

```bash
python manage.py makemigrations 
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## 🧱 Архитектура проекта

```
apps/
  users/
  catalog/
  warehouses/
  inventory/
  ore/
  thresholds/
  stockpiles/
  inventory_count/
  sync/
  reports/
  procurement/
  transport/
templates/
static/
media/
```

---

## 📘 Описание моделей (по приложениям)

Ниже перечислены все модели проекта с кратким описанием и основными полями.  
Структура разделена по приложениям (apps/*).

---

### 🔹 `apps/users` — пользователи и роли

**User** — расширение стандартного `AbstractUser`.  
Дополнительные поля:
- `full_name` — ФИО пользователя;  
- `role` — роль (`ADMIN`, `OPERATOR`, `WAREHOUSE`, `ANALYST`).  

Используется в связях `created_by`, `actor`.  
⚙️ Настройка:  
```python
AUTH_USER_MODEL = "users.User"
```

---

### 🔹 `apps/catalog` — справочники

**Uom** — единицы измерения (`code`, `name`), например: `KG`, `TON`, `PCS`.  
**Item** — номенклатура (`sku`, `name`, `description`, `base_uom`).  
**Supplier** — поставщики (`code`, `name`, `tax_id`, `is_active`). Используется в закупках.

---

### 🔹 `apps/warehouses` — склады и локации

**Warehouse** — склад/цех (`code`, `name`).  
**Location** — место хранения (`warehouse`, `code`, `name`),  
уникальность — пара `(warehouse, code)`.

---

### 🔹 `apps/inventory` — остатки и движения

**Inventory** — текущие остатки по связке `(location, item)` + `qty_on_hand`, `uom`.  
**Movement** — журнал операций:  
`type`, `occurred_at`, `item`, `from_location`, `to_location`, `qty`, `uom`, `actor`, `note`.  

Используется для всех движений: приёмка, списание, перемещение, корректировка.

---

### 🔹 `apps/ore` — приёмка руды

**OreReceipt** — документ приёмки руды:  
`location`, `item`, `quantity`, `contract`, `created_at`, `created_by`.  

После сохранения создаёт запись `Movement(type=RECEIPT)`  
и обновляет `Inventory`.

---

### 🔹 `apps/thresholds` — пороги и алерты

**Threshold** — нормы минимум/максимум для остатков:  
`warehouse`, `location?`, `item`, `min_qty`, `max_qty`, `uom`, `is_active`.  

**Alert** — нарушения порогов:  
`warehouse`, `location?`, `item`, `current_qty`, `uom`, `severity`, `state`, `correlation_id`, `message`.  

Создаётся автоматически при выходе остатков за пределы нормы.

---

### 🔹 `apps/stockpiles` — кучи / резервуары

**Stockpile** — объект хранения (куча, резервуар):  
`warehouse`, `code`, `name`, `capacity_qty`, `uom`.  

**StockpileThreshold** — пороги (`min_qty`, `max_qty`, `is_active`).  
**StockpileAlert** — уведомления (`current_qty`, `severity`, `state`, `created_at`).

---

### 🔹 `apps/inventory_count` — инвентаризации

**InventoryCount** — акт инвентаризации:  
`number`, `warehouse`, `status`, `created_at`, `created_by`.  

**InventoryCountLine** — строки акта:  
`count`, `location`, `item`, `qty_book`, `qty_fact`, `delta`, `note`.  

После закрытия документа можно сформировать корректирующие `Movement(type=ADJUSTMENT)`.

---

### 🔹 `apps/sync` — очередь синхронизации

**SyncQueue** — оффлайн-очередь обмена:  
`entity`, `operation`, `payload`, `correlation_id`,  
`state (PENDING/SENT/ACK/ERROR)`, `retry_count`, `last_error`,  
`created_at`, `updated_at`.  

Используется для оффлайн-режима и устойчивых интеграций.

---

### 🔹 `apps/reports` — журнал отчётов

**CalcLog** — журнал фоновых расчётов и отчётов:  
`calc_type`, `params`, `started_at`, `finished_at`,  
`status (RUNNING/SUCCESS/FAILED)`, `rows_read`, `rows_written`,  
`result_ref`, `error_message`.  

Позволяет контролировать выполнение отчётов и хранить результаты (PDF, Excel и т.д.).

---

### 🔹 `apps/procurement` — закупки

**PurchaseRequest** — заявка на закупку:  
`number`, `item`, `qty`, `uom`, `warehouse`, `supplier?`,  
`state (DRAFT/SUBMITTED/APPROVED/ORDERED/CLOSED/REJECTED)`,  
`comment`, `attachment`, `created_at`, `created_by`.  

Жизненный цикл заявки — от черновика до закрытия/отклонения.

---

### 🔹 `apps/transport` — транспорт и поставки

**TransportUnit** — транспортная единица (`type`, `number`).  
**Arrival** — факт прибытия (`unit`, `route_no`, `arrived_at`).  
**ArrivalLine** — строки поставки (`arrival`, `item`, `qty`, `uom`, `location`).  

Может быть связана с автоматической приёмкой (`OreReceipt`) и движением (`Movement`).

---

## ⚙️ Миграции и суперпользователь

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

---

## 🔐 Доступ и роли

Используются стандартные Django Permissions и Groups.  
Группы: Администратор, Кладовщик, Оператор, Аналитик.

---


## Контрольный чек-лист соответствия ТЗ

✅ Склады, локации, остатки, движения  
✅ Приёмка руды, списание, перемещения  
✅ Контроль порогов и уведомления  
✅ Инвентаризация  
✅ Заявки на закупку  
✅ Учёт транспорта и поставок  
✅ Очередь синхронизации  
✅ Журнал отчётов и аналитики  
✅ Роли и права доступа  

---
