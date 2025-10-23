from django.contrib import admin
from .models import Warehouse, Location


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("code", "name")
    ordering = ("name",)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "warehouse")
    list_filter = ("warehouse",)
    search_fields = ("code", "name", "warehouse__name")
    ordering = ("warehouse__name", "code")
