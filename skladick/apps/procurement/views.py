from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.catalog.models import Item
from apps.ore.models import OreReceipt

from .forms import PurchaseRequestForm
from .models import PurchaseRequest


class PurchaseRequestListView(LoginRequiredMixin, ListView):
    """Список заявок на закупку."""

    model = PurchaseRequest
    context_object_name = "purchase_requests"
    template_name = "procurement/purchase_request_list.html"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        query = self.request.GET.copy()
        if "page" in query:
            query.pop("page")
        ctx["querystring"] = query.urlencode()
        return ctx


class PurchaseRequestDetailView(LoginRequiredMixin, DetailView):
    """Просмотр заявки на закупку."""

    model = PurchaseRequest
    context_object_name = "purchase_request"
    template_name = "procurement/purchase_request_detail.html"


class PurchaseRequestCreateView(LoginRequiredMixin, CreateView):
    """Создание новой заявки на закупку."""

    model = PurchaseRequest
    form_class = PurchaseRequestForm
    template_name = "procurement/purchase_request_form.html"
    success_url = reverse_lazy("procurement:purchase_request_list")

    def form_valid(self, form):
        if self.request.user.is_authenticated:
            form.instance.created_by = self.request.user
        return super().form_valid(form)


class PurchaseRequestUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование существующей заявки."""

    model = PurchaseRequest
    form_class = PurchaseRequestForm
    template_name = "procurement/purchase_request_form.html"
    success_url = reverse_lazy("procurement:purchase_request_list")


class PurchaseRequestStatusChangeView(LoginRequiredMixin, View):
    """Изменение статуса заявки и автоматическое создание приёмки при утверждении."""

    def post(self, request, pk, action):
        pr = get_object_or_404(PurchaseRequest, pk=pk)

        # --- Отправка на утверждение ---
        if action == "submit" and pr.state == "DRAFT":
            pr.state = "SUBMITTED"
            msg = f"Заявка {pr.number} отправлена на утверждение."

        # --- Утверждение заявки ---
        elif action == "approve" and pr.state == "SUBMITTED":
            pr.state = "APPROVED"
            msg = f"Заявка {pr.number} утверждена."

            if pr.item.kind == Item.ORE:
                try:
                    loc = pr.warehouse.location_set.first()  # первая локация склада
                    if not loc:
                        messages.warning(
                            request,
                            f"⚠️ У склада '{pr.warehouse}' нет локаций, приёмка не создана.",
                        )
                    else:
                        OreReceipt.objects.create(
                            location=loc,
                            item=pr.item,
                            quantity=pr.qty,
                            contract=f"Закупка {pr.number}",
                            created_by=request.user,
                        )
                        messages.success(
                            request,
                            f"✅ Создан акт приёмки по заявке {pr.number} ({pr.qty} {pr.uom.code})",
                        )
                except Exception as e:
                    messages.error(request, f"Ошибка при создании приёмки: {e}")

        # --- Отклонение заявки ---
        elif action == "reject" and pr.state in ["SUBMITTED", "APPROVED"]:
            pr.state = "REJECTED"
            msg = f"Заявка {pr.number} отклонена."

        # --- Некорректные переходы ---
        else:
            messages.warning(request, "Недопустимое действие для текущего статуса.")
            return redirect("procurement:purchase_request_detail", pk=pk)

        pr.save(update_fields=["state"])
        messages.info(request, msg)
        return redirect("procurement:purchase_request_detail", pk=pk)
