from django.contrib import admin
from .models import LeaveType, LeaveRequest, LeaveBalance


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "max_days", "description")
    search_fields = ("name",)


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "leave_type",
        "start_date",
        "end_date",
        "status",
        "approved_by",
        "applied_at",
    )
    list_filter = ("status", "leave_type", "applied_at")
    search_fields = ("employee__username", "employee__employee_id", "reason")
    date_hierarchy = "applied_at"
    ordering = ("-applied_at",)


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ("employee", "leave_type", "days_remaining")
    search_fields = ("employee__username", "employee__employee_id", "leave_type__name")
    list_filter = ("leave_type",)
