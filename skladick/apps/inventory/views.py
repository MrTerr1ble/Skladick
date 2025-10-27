from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from django.utils.timezone import make_aware
from datetime import datetime
from .models import Inventory, Movement
from .forms import MovementForm


class InventoryListView(LoginRequiredMixin, ListView):
    model = Inventory
    template_name = "inventory/inventory_list.html"
    context_object_name = "rows"
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset().select_related("location__warehouse", "item", "uom")
        w = self.request.GET.get("warehouse")
        i = self.request.GET.get("item")
        kind = self.request.GET.get("kind")
        if w:
            qs = qs.filter(location__warehouse__id=w)
        if kind:
            qs = qs.filter(item__kind=kind)
        if i:
            qs = qs.filter(item__id=i)
        return qs

    def get_context_data(self, **kwargs):
        from apps.warehouses.models import Warehouse
        from apps.catalog.models import Item
        ctx = super().get_context_data(**kwargs)
        ctx["warehouses"] = Warehouse.objects.all().order_by("name")
        kind = self.request.GET.get("kind")
        items = Item.objects.all().order_by("name")
        if kind:
            items = items.filter(kind=kind)
        ctx["items"] = items[:500]
        ctx["kinds"] = Item.KINDS
        query = self.request.GET.copy()
        if "page" in query:
            query.pop("page")
        ctx["querystring"] = query.urlencode()
        return ctx


class MovementListView(LoginRequiredMixin, ListView):
    """Список перемещений/списаний/приходов с фильтрами."""
    model = Movement
    template_name = "inventory/movement_list.html"
    context_object_name = "moves"
    paginate_by = 50
    ordering = "-occurred_at"

    def get_queryset(self):
        qs = super().get_queryset().select_related(
            "item", "uom", "from_location__warehouse", "to_location__warehouse", "actor"
        )
        t = self.request.GET.get("type")
        i = self.request.GET.get("item")
        w = self.request.GET.get("warehouse")
        d1 = self.request.GET.get("date_from")
        d2 = self.request.GET.get("date_to")

        if t: qs = qs.filter(type=t)
        if i: qs = qs.filter(item_id=i)
        if w: qs = qs.filter(
            # либо со склада-источника, либо со склада-приёмника
            # (если нужно строго один — сузим)
            models.Q(from_location__warehouse_id=w) | models.Q(to_location__warehouse_id=w)
        )
        try:
            if d1:
                qs = qs.filter(occurred_at__gte=make_aware(datetime.fromisoformat(d1)))
            if d2:
                qs = qs.filter(occurred_at__lte=make_aware(datetime.fromisoformat(d2 + " 23:59:59")))
        except Exception:
            pass
        return qs

    def get_context_data(self, **kwargs):
        from apps.warehouses.models import Warehouse
        from apps.catalog.models import Item
        ctx = super().get_context_data(**kwargs)
        ctx["types"] = Movement.TYPES
        ctx["warehouses"] = Warehouse.objects.all().order_by("name")
        ctx["items"] = Item.objects.all().order_by("name")[:500]
        query = self.request.GET.copy()
        if "page" in query:
            query.pop("page")
        ctx["querystring"] = query.urlencode()
        return ctx


class MovementCreateView(LoginRequiredMixin, CreateView):
    """Создание движения (перемещение/списание/приход)."""
    model = Movement
    form_class = MovementForm
    template_name = "inventory/movement_form.html"
    success_url = reverse_lazy("inventory:movement_list")

    def form_valid(self, form):
        form.instance.actor = self.request.user
        return super().form_valid(form)
