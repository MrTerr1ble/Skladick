from django.urls import path

from .views import (
    PurchaseRequestCreateView,
    PurchaseRequestDetailView,
    PurchaseRequestListView,
    PurchaseRequestUpdateView,
    PurchaseRequestStatusChangeView
)


app_name = "procurement"


urlpatterns = [
    path("", PurchaseRequestListView.as_view(), name="purchase_request_list"),
    path("create/", PurchaseRequestCreateView.as_view(), name="purchase_request_create"),
    path("<int:pk>/", PurchaseRequestDetailView.as_view(), name="purchase_request_detail"),
    path("<int:pk>/edit/", PurchaseRequestUpdateView.as_view(), name="purchase_request_update"),
    path("<int:pk>/status/<str:action>/", PurchaseRequestStatusChangeView.as_view(), name="purchase_request_status_change"),
]