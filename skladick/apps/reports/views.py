from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.views.generic import TemplateView

from apps.inventory.models import Inventory
from apps.ore.models import OreReceipt
from apps.procurement.models import PurchaseRequest
from apps.thresholds.models import Alert


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

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

        return context
