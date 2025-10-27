from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.views import View

from .forms import PurchaseRequestForm
from .models import PurchaseRequest


class PurchaseRequestListView(LoginRequiredMixin, ListView):
    """Список заявок на закупку."""

    model = PurchaseRequest
    context_object_name = "purchase_requests"
    template_name = "procurement/purchase_request_list.html"
    paginate_by = 20


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
    """Изменение статуса заявки (отправить, утвердить, отклонить)."""

    def post(self, request, pk, action):
        pr = get_object_or_404(PurchaseRequest, pk=pk)
        # простая логика переходов
        if action == "submit" and pr.state == "DRAFT":
            pr.state = "SUBMITTED"
            msg = "Заявка отправлена на рассмотрение."
        elif action == "approve" and pr.state == "SUBMITTED":
            pr.state = "APPROVED"
            msg = "Заявка утверждена."
        elif action == "reject" and pr.state in ["SUBMITTED", "APPROVED"]:
            pr.state = "REJECTED"
            msg = "Заявка отклонена."
        else:
            messages.warning(request, "Недопустимое действие.")
            return redirect("procurement:purchase_request_detail", pk=pk)

        pr.save(update_fields=["state"])
        messages.success(request, msg)
        return redirect("procurement:purchase_request_detail", pk=pk)
