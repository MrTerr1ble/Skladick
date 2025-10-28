from django.contrib import admin

from apps.catalog.models import Item

from .models import Inventory, Movement


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("location", "item", "qty_on_hand", "uom")
    list_filter = ("location__warehouse", "location", "uom")
    search_fields = ("item__sku", "item__name", "location__code", "location__warehouse__name")
    ordering = ("location__warehouse__name", "location__code")
    autocomplete_fields = ("location", "item", "uom")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(item__kind=Item.ORE)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "item":
            kwargs.setdefault("queryset", db_field.related_model.objects.exclude(kind=Item.ORE))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Movement)
class MovementAdmin(admin.ModelAdmin):
    list_display = ("type", "occurred_at", "item", "qty", "uom", "serial_number", "actor")
    list_filter = ("type", "item__kind", "item", "uom", "occurred_at")
    search_fields = ("item__sku", "item__name", "actor__username", "serial_number")
    date_hierarchy = "occurred_at"
    ordering = ("-occurred_at",)
    autocomplete_fields = ("item", "from_location", "to_location", "uom", "actor")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(item__kind=Item.ORE)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "item":
            kwargs.setdefault("queryset", db_field.related_model.objects.exclude(kind=Item.ORE))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
