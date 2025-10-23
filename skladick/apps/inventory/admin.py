from django.contrib import admin
from .models import Inventory, Movement


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("location", "item", "qty_on_hand", "uom")
    list_filter = ("location__warehouse", "location", "uom")
    search_fields = ("item__sku", "item__name", "location__code", "location__warehouse__name")
    ordering = ("location__warehouse__name", "location__code")
    autocomplete_fields = ("location", "item", "uom")


@admin.register(Movement)
class MovementAdmin(admin.ModelAdmin):
    list_display = ("type", "occurred_at", "item", "qty", "uom", "actor")
    list_filter = ("type", "item", "uom", "occurred_at")
    search_fields = ("item__sku", "item__name", "actor__username")
    date_hierarchy = "occurred_at"
    ordering = ("-occurred_at",)
    autocomplete_fields = ("item", "from_location", "to_location", "uom", "actor")
