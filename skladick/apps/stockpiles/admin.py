from django.contrib import admin

from .models import (
    Stockpile,
    StockpileAlert,
    StockpileInventory,
    StockpileMovement,
    StockpileThreshold,
)


@admin.register(Stockpile)
class StockpileAdmin(admin.ModelAdmin):
    list_display = ("warehouse", "location", "code", "name")
    list_filter = ("warehouse",)
    search_fields = ("code", "name", "warehouse__name")
    autocomplete_fields = ("warehouse", "location")
    ordering = ("warehouse__name", "code")


@admin.register(StockpileInventory)
class StockpileInventoryAdmin(admin.ModelAdmin):
    list_display = ("stockpile", "item", "qty_on_ground", "uom")
    list_filter = ("stockpile__warehouse", "item")
    search_fields = ("stockpile__code", "stockpile__warehouse__name", "item__name")
    autocomplete_fields = ("stockpile", "item", "uom")


@admin.register(StockpileMovement)
class StockpileMovementAdmin(admin.ModelAdmin):
    list_display = (
        "movement_type",
        "occurred_at",
        "item",
        "qty",
        "uom",
        "from_stockpile",
        "to_stockpile",
        "actor",
    )
    list_filter = ("movement_type", "item", "from_stockpile__warehouse", "to_stockpile__warehouse")
    search_fields = (
        "item__sku",
        "item__name",
        "from_stockpile__code",
        "to_stockpile__code",
        "actor__username",
    )
    date_hierarchy = "occurred_at"
    autocomplete_fields = ("item", "from_stockpile", "to_stockpile", "uom", "actor")
    ordering = ("-occurred_at",)


@admin.register(StockpileThreshold)
class StockpileThresholdAdmin(admin.ModelAdmin):
    list_display = ("stockpile", "item", "min_qty", "max_qty", "uom", "is_active")
    list_filter = ("is_active", "stockpile__warehouse")
    search_fields = ("stockpile__code", "stockpile__warehouse__name", "item__name")
    autocomplete_fields = ("stockpile", "item", "uom")


@admin.register(StockpileAlert)
class StockpileAlertAdmin(admin.ModelAdmin):
    list_display = ("state", "stockpile", "item", "current_qty", "uom", "created_at")
    list_filter = ("state", "stockpile__warehouse", "item")
    search_fields = ("stockpile__code", "stockpile__warehouse__name", "item__name")
    date_hierarchy = "created_at"
    autocomplete_fields = ("stockpile", "item", "uom")
    ordering = ("-created_at",)
