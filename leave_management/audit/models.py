from django.db import models
from django.conf import settings
from leave.models import LeaveRequest


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ("SUBMIT", "Submit Leave Request"),
        ("APPROVE", "Approve Leave Request"),
        ("REJECT", "Reject Leave Request"),
        ("CANCEL", "Cancel Leave Request"),
    ]

    leave_request = models.ForeignKey(
        LeaveRequest,
        on_delete=models.CASCADE,
        related_name="audit_logs"
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="performed_audits"
    )
    performed_at = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(blank=True)  # optional justification

    class Meta:
        ordering = ["-performed_at"]

    def __str__(self):
        return f"{self.leave_request} - {self.action} by {self.performed_by}"
