from django.urls import path
from .views import ReceiptListView, ReceiptCreateView

app_name = "ore"

urlpatterns = [
    path("", ReceiptListView.as_view(), name="receipt_list"),
    path("new/", ReceiptCreateView.as_view(), name="receipt_create"),
]
