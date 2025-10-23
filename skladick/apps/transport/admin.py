from django.contrib import admin
from .models import TransportUnit, Arrival, ArrivalLine


class ArrivalLineInline(admin.TabularInline):
    model = ArrivalLine
    extra = 0
    autocomplete_fields = ("item", "uom", "location")
    fields = ("item", "qty", "uom", "location")


@admin.register(TransportUnit)
class TransportUnitAdmin(admin.ModelAdmin):
    list_display = ("type", "number")
    list_filter = ("type",)
    search_fields = ("number",)
    ordering = ("type", "number")


@admin.register(Arrival)
class ArrivalAdmin(admin.ModelAdmin):
    list_display = ("unit", "route_no", "arrived_at")
    list_filter = ("unit__type",)
    search_fields = ("unit__number", "route_no")
    date_hierarchy = "arrived_at"
    autocomplete_fields = ("unit",)
    inlines = [ArrivalLineInline]
    ordering = ("-arrived_at",)


@admin.register(ArrivalLine)
class ArrivalLineAdmin(admin.ModelAdmin):
    list_display = ("arrival", "item", "qty", "uom", "location")
    list_filter = ("arrival__unit__type", "location__warehouse")
    search_fields = ("arrival__unit__number", "item__sku", "item__name", "location__code")
    autocomplete_fields = ("arrival", "item", "uom", "location")
