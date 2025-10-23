from django.contrib import admin
from .models import InventoryCount, InventoryCountLine


class InventoryCountLineInline(admin.TabularInline):
    model = InventoryCountLine
    extra = 0
    autocomplete_fields = ("location", "item")
    fields = ("location", "item", "qty_book", "qty_fact", "delta", "note")


@admin.register(InventoryCount)
class InventoryCountAdmin(admin.ModelAdmin):
    list_display = ("number", "warehouse", "status", "created_at", "created_by")
    list_filter = ("status", "warehouse")
    search_fields = ("number", "warehouse__name", "created_by__username")
    date_hierarchy = "created_at"
    autocomplete_fields = ("warehouse", "created_by")
    inlines = [InventoryCountLineInline]
    ordering = ("-created_at",)


@admin.register(InventoryCountLine)
class InventoryCountLineAdmin(admin.ModelAdmin):
    list_display = ("count", "location", "item", "qty_book", "qty_fact", "delta")
    list_filter = ("count__warehouse", "count__status")
    search_fields = ("count__number", "location__code", "item__sku", "item__name")
    autocomplete_fields = ("count", "location", "item")
    ordering = ("count__number", "location__code", "item__name")
