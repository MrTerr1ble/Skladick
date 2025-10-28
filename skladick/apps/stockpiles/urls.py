from django.urls import path

from .views import StockpileDashboardView

app_name = "stockpiles"

urlpatterns = [
    path("", StockpileDashboardView.as_view(), name="dashboard"),
]
