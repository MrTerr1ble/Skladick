from django.contrib import admin

from apps.catalog.models import Item

from .models import Alert, Threshold


@admin.register(Threshold)
class ThresholdAdmin(admin.ModelAdmin):
    list_display = ("warehouse", "location", "item", "min_qty", "max_qty", "uom", "is_active", "created_at")
    list_filter = ("warehouse", "location", "item", "is_active")
    search_fields = ("warehouse__name", "location__code", "item__sku", "item__name")
    autocomplete_fields = ("warehouse", "location", "item", "uom")
    ordering = ("warehouse__name", "location__code", "item__name")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(item__kind=Item.ORE)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "item":
            kwargs.setdefault("queryset", db_field.related_model.objects.exclude(kind=Item.ORE))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ("state", "severity", "warehouse", "location", "item", "current_qty", "uom", "created_at")
    list_filter = ("state", "severity", "warehouse", "location", "item")
    search_fields = ("item__sku", "item__name", "warehouse__name", "location__code", "correlation_id")
    date_hierarchy = "created_at"
    autocomplete_fields = ("warehouse", "location", "item", "uom", "threshold")
    ordering = ("-created_at",)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(item__kind=Item.ORE)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "item":
            kwargs.setdefault("queryset", db_field.related_model.objects.exclude(kind=Item.ORE))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
