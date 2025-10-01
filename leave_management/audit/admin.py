from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("leave_request", "action", "performed_by", "performed_at")
    list_filter = ("action", "performed_at")
    search_fields = ("leave_request__employee__username", "performed_by__username")
    date_hierarchy = "performed_at"
