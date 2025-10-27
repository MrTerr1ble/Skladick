from django.urls import path

from .views import (
    PurchaseRequestCreateView,
    PurchaseRequestDetailView,
    PurchaseRequestListView,
    PurchaseRequestUpdateView,
)


app_name = "procurement"


urlpatterns = [
    path("", PurchaseRequestListView.as_view(), name="purchase_request_list"),
    path("create/", PurchaseRequestCreateView.as_view(), name="purchase_request_create"),
    path("<int:pk>/", PurchaseRequestDetailView.as_view(), name="purchase_request_detail"),
    path("<int:pk>/edit/", PurchaseRequestUpdateView.as_view(), name="purchase_request_update"),
]

