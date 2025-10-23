from django.contrib import admin
from .models import Uom, Item, Supplier


@admin.register(Uom)
class UomAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")
    ordering = ("code",)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ("sku", "name", "base_uom")
    list_filter = ("base_uom",)
    search_fields = ("sku", "name", "description")
    ordering = ("sku",)
    autocomplete_fields = ("base_uom",)


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "tax_id", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name", "tax_id")
    ordering = ("name",)
