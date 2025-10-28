from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .models import StockpileAlert, StockpileInventory


class StockpileDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "stockpiles/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["inventories"] = (
            StockpileInventory.objects.select_related("stockpile__warehouse", "item", "uom")
            .order_by("stockpile__warehouse__name", "stockpile__code", "item__name")
        )
        ctx["alerts"] = (
            StockpileAlert.objects.select_related("stockpile__warehouse", "item", "uom")
            .order_by("-created_at")
        )
        return ctx
