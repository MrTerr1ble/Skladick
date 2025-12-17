import json
from decimal import Decimal
from datetime import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.views.generic import TemplateView

from apps.inventory.models import Inventory, Movement
from apps.ore.models import OreReceipt
from apps.procurement.models import PurchaseRequest
from apps.thresholds.models import Alert
from apps.warehouses.models import Warehouse


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # --- Основные метрики ---
        inventory_total = Inventory.objects.aggregate(total=Sum("qty_on_hand"))["total"]
        context["inventory_total"] = inventory_total or Decimal("0")

        context["open_alerts_count"] = Alert.objects.filter(state=Alert.OPEN).count()

        context["active_purchase_requests_count"] = PurchaseRequest.objects.filter(
            state__in=[PurchaseRequest.SUBMITTED, PurchaseRequest.APPROVED]
        ).count()

        context["recent_receipts"] = (
            OreReceipt.objects.select_related("location", "location__warehouse", "item", "created_by")
            .order_by("-created_at")[:5]
        )

        # --- Данные для графиков ---

        # 1. Приёмки по дням (последние 14 дней)
        today = timezone.now().date()
        start_date = today - timedelta(days=13)
        
        receipts_by_day = (
            OreReceipt.objects
            .filter(created_at__date__gte=start_date)
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"), total_qty=Sum("quantity"))
            .order_by("day")
        )
        
        # Создаём полный список дней
        receipts_dict = {r["day"]: {"count": r["count"], "qty": float(r["total_qty"] or 0)} for r in receipts_by_day}
        receipts_labels = []
        receipts_counts = []
        receipts_qty = []
        
        for i in range(14):
            day = start_date + timedelta(days=i)
            receipts_labels.append(day.strftime("%d.%m"))
            data = receipts_dict.get(day, {"count": 0, "qty": 0})
            receipts_counts.append(data["count"])
            receipts_qty.append(data["qty"])

        context["receipts_chart"] = json.dumps({
            "labels": receipts_labels,
            "counts": receipts_counts,
            "qty": receipts_qty,
        })

        # 2. Остатки по складам
        inventory_by_warehouse = (
            Inventory.objects
            .values("location__warehouse__name")
            .annotate(total=Sum("qty_on_hand"))
            .order_by("-total")
        )
        
        warehouse_labels = []
        warehouse_data = []
        for item in inventory_by_warehouse:
            name = item["location__warehouse__name"] or "Без склада"
            warehouse_labels.append(name)
            warehouse_data.append(float(item["total"] or 0))

        context["warehouse_chart"] = json.dumps({
            "labels": warehouse_labels,
            "data": warehouse_data,
        })

        # 3. Движения по типам (за последние 30 дней)
        month_ago = timezone.now() - timedelta(days=30)
        movements_by_type = (
            Movement.objects
            .filter(occurred_at__gte=month_ago)
            .values("type")
            .annotate(count=Count("id"))
        )
        
        type_labels_map = dict(Movement.TYPES)
        movement_labels = []
        movement_data = []
        for item in movements_by_type:
            movement_labels.append(type_labels_map.get(item["type"], item["type"]))
            movement_data.append(item["count"])

        context["movements_chart"] = json.dumps({
            "labels": movement_labels,
            "data": movement_data,
        })

        # 4. Статусы заявок на закупку
        requests_by_status = (
            PurchaseRequest.objects
            .values("state")
            .annotate(count=Count("id"))
        )
        
        state_labels_map = {
            PurchaseRequest.DRAFT: "Черновик",
            PurchaseRequest.SUBMITTED: "На рассмотрении",
            PurchaseRequest.APPROVED: "Утверждена",
            PurchaseRequest.REJECTED: "Отклонена",
        }
        
        status_labels = []
        status_data = []
        for item in requests_by_status:
            status_labels.append(state_labels_map.get(item["state"], item["state"]))
            status_data.append(item["count"])

        context["requests_chart"] = json.dumps({
            "labels": status_labels,
            "data": status_data,
        })

        # 5. Дополнительные метрики
        context["total_movements_month"] = Movement.objects.filter(occurred_at__gte=month_ago).count()
        context["total_warehouses"] = Warehouse.objects.count()

        return context
