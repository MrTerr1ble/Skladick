from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView
from .models import OreReceipt
from .forms import OreReceiptForm


class ReceiptListView(LoginRequiredMixin, ListView):
    model = OreReceipt
    template_name = "ore/receipt_list.html"
    context_object_name = "receipts"
    paginate_by = 20
    ordering = "-created_at"


class ReceiptCreateView(LoginRequiredMixin, CreateView):
    model = OreReceipt
    form_class = OreReceiptForm
    template_name = "ore/receipt_form.html"
    success_url = reverse_lazy("ore:receipt_list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)
