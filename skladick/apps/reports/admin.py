from django.contrib import admin
from .models import CalcLog


@admin.register(CalcLog)
class CalcLogAdmin(admin.ModelAdmin):
    list_display = ("calc_type", "status", "started_at", "finished_at", "rows_read", "rows_written", "result_ref")
    list_filter = ("status", "calc_type")
    search_fields = ("calc_type", "result_ref", "error_message")
    date_hierarchy = "started_at"
    ordering = ("-started_at",)
    readonly_fields = ("started_at", "finished_at")
