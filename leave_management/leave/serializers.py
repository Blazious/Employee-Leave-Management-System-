from rest_framework import serializers
from .models import LeaveType, LeaveRequest, LeaveBalance
from .utils import calculate_leave_days
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = ["id", "name", "description", "max_days"]


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee = serializers.SlugRelatedField(
        slug_field="employee_id",
        queryset=User.objects.all(),
        required=False,
        default=serializers.CurrentUserDefault()
    )
    total_days = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "employee",
            "leave_type",
            "start_date",
            "end_date",
            "reason",
            "status",
            "applied_at",
            "updated_at",
            "approved_by",
            "comments",
            "total_days",
        ]
        read_only_fields = ["status", "applied_at", "updated_at", "approved_by", "total_days"]

    def get_total_days(self, obj):
        if obj.start_date and obj.end_date:
            # Use the proper function that excludes weekends and holidays
            return calculate_leave_days(obj.start_date, obj.end_date)
        return 0


class LeaveBalanceSerializer(serializers.ModelSerializer):
    employee = serializers.SlugRelatedField(
        slug_field="employee_id",
        queryset=User.objects.all()
    )
    leave_type = serializers.SlugRelatedField(
        slug_field="name",
        queryset=LeaveType.objects.all()
    )

    class Meta:
        model = LeaveBalance
        fields = ["id", "employee", "leave_type", "days_remaining"]
