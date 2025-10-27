from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

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

