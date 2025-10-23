from django.contrib import admin
from .models import PurchaseRequest


@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ("number", "item", "qty", "uom", "warehouse", "state", "created_at", "created_by")
    list_filter = ("state", "warehouse", "uom", "item")
    search_fields = ("number", "item__sku", "item__name", "warehouse__name", "created_by__username")
    date_hierarchy = "created_at"
    autocomplete_fields = ("item", "uom", "warehouse", "supplier", "created_by")
    ordering = ("-created_at",)
