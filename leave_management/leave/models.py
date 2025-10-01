from django.db import models
from django.conf import settings


class LeaveType(models.Model):
    """Different types of leave (Annual, Sick, Emergency, etc.)."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    max_days = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Optional limit for this leave type (per year)."
    )

    def __str__(self):
        return self.name


class LeaveRequest(models.Model):
    """Main leave request model."""
    STATUS_PENDING = "PENDING"
    STATUS_APPROVED = "APPROVED"
    STATUS_REJECTED = "REJECTED"
    STATUS_CANCELLED = "CANCELLED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="leave_requests"
    )
    leave_type = models.ForeignKey(
        LeaveType,
        on_delete=models.SET_NULL,
        null=True,
        related_name="leave_requests"
    )
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="approved_leaves",
        help_text="The manager/HR who approved this leave"
    )
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.employee.employee_id} - {self.leave_type} ({self.status})"


# Track yearly leave balance
class LeaveBalance(models.Model):
    """Track how many days remain for each employee and leave type."""
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="leave_balances"
    )
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    days_remaining = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ("employee", "leave_type")

    def __str__(self):
        return f"{self.employee.employee_id} - {self.leave_type}: {self.days_remaining} days left"
