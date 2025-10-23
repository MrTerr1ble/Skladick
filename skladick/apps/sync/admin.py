from django.contrib import admin
from .models import SyncQueue


@admin.register(SyncQueue)
class SyncQueueAdmin(admin.ModelAdmin):
    list_display = ("entity", "operation", "state", "retry_count", "correlation_id", "created_at", "updated_at")
    list_filter = ("state", "entity", "operation")
    search_fields = ("correlation_id", "entity")
    date_hierarchy = "created_at"
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
