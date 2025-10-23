from django.contrib import admin
from .models import Stockpile, StockpileThreshold, StockpileAlert


@admin.register(Stockpile)
class StockpileAdmin(admin.ModelAdmin):
    list_display = ("warehouse", "code", "name", "capacity_qty", "uom")
    list_filter = ("warehouse",)
    search_fields = ("code", "name", "warehouse__name")
    autocomplete_fields = ("warehouse", "uom")
    ordering = ("warehouse__name", "code")


@admin.register(StockpileThreshold)
class StockpileThresholdAdmin(admin.ModelAdmin):
    list_display = ("stockpile", "min_qty", "max_qty", "is_active")
    list_filter = ("is_active",)
    search_fields = ("stockpile__code", "stockpile__warehouse__name")
    autocomplete_fields = ("stockpile",)


@admin.register(StockpileAlert)
class StockpileAlertAdmin(admin.ModelAdmin):
    list_display = ("state", "severity", "stockpile", "current_qty", "created_at")
    list_filter = ("state", "severity", "stockpile__warehouse")
    search_fields = ("stockpile__code", "stockpile__warehouse__name")
    date_hierarchy = "created_at"
    autocomplete_fields = ("stockpile",)
    ordering = ("-created_at",)
