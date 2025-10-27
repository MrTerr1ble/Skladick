from django.urls import path
from .views import InventoryListView, MovementListView, MovementCreateView

app_name = "inventory"

urlpatterns = [
    path("", InventoryListView.as_view(), name="inventory_list"),
    path("movements/", MovementListView.as_view(), name="movement_list"),
    path("movements/new/", MovementCreateView.as_view(), name="movement_create"),
]
