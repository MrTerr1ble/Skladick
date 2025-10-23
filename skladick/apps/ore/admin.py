from django.contrib import admin
from .models import OreReceipt


@admin.register(OreReceipt)
class OreReceiptAdmin(admin.ModelAdmin):
    list_display = ("item", "quantity", "location", "created_at", "created_by")
    list_filter = ("item", "location__warehouse", "created_at")
    search_fields = ("item__sku", "item__name", "location__code", "location__warehouse__name", "created_by__username")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    autocomplete_fields = ("item", "location", "created_by")
