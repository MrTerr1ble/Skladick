from django.contrib import admin
from .models import Threshold, Alert


@admin.register(Threshold)
class ThresholdAdmin(admin.ModelAdmin):
    list_display = ("warehouse", "location", "item", "min_qty", "max_qty", "uom", "is_active", "created_at")
    list_filter = ("warehouse", "location", "item", "is_active")
    search_fields = ("warehouse__name", "location__code", "item__sku", "item__name")
    autocomplete_fields = ("warehouse", "location", "item", "uom")
    ordering = ("warehouse__name", "location__code", "item__name")

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ("state", "severity", "warehouse", "location", "item", "current_qty", "uom", "created_at")
    list_filter = ("state", "severity", "warehouse", "location", "item")
    search_fields = ("item__sku", "item__name", "warehouse__name", "location__code", "correlation_id")
    date_hierarchy = "created_at"
    autocomplete_fields = ("warehouse", "location", "item", "uom", "threshold")
    ordering = ("-created_at",)
