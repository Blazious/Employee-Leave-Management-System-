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
        "total_days",
        "status",
        "approved_by",
        "applied_at",
    )
    list_filter = ("status", "leave_type", "applied_at")
    search_fields = ("employee__username", "employee__employee_id", "reason")
    date_hierarchy = "applied_at"
    ordering = ("-applied_at",)
    readonly_fields = ("applied_at", "total_days")
    actions = ["approve_leaves", "reject_leaves"]

    def total_days(self, obj):
        """Calculate total working days excluding weekends and holidays"""
        from .utils import calculate_leave_days
        return calculate_leave_days(obj.start_date, obj.end_date)
    total_days.short_description = "Working Days"

    def approve_leaves(self, request, queryset):
        from .utils import send_leave_status_update_email
        for leave in queryset:
            if leave.status == "PENDING":
                leave.status = "APPROVED"
                leave.approved_by = request.user
                leave.save()
                # Send email notification
                send_leave_status_update_email(leave, "APPROVED")
        self.message_user(request, f"{queryset.count()} leave request(s) have been approved.")
    approve_leaves.short_description = "Approve selected leave requests"

    def reject_leaves(self, request, queryset):
        from .utils import send_leave_status_update_email
        for leave in queryset:
            if leave.status == "PENDING":
                leave.status = "REJECTED"
                leave.approved_by = request.user
                leave.save()
                # Send email notification
                send_leave_status_update_email(leave, "REJECTED")
        self.message_user(request, f"{queryset.count()} leave request(s) have been rejected.")
    reject_leaves.short_description = "Reject selected leave requests"

    def save_model(self, request, obj, form, change):
        if not change:  # If this is a new leave request
            from .utils import send_leave_request_email
            obj.employee = request.user  # Set the current user as employee
        super().save_model(request, obj, form, change)
        if not change:  # If this is a new leave request
            send_leave_request_email(obj)  # Send email notification


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ("employee", "leave_type", "days_remaining")
    search_fields = ("employee__username", "employee__employee_id", "leave_type__name")
    list_filter = ("leave_type",)
