from rest_framework import serializers
from .models import AuditLog
from user.serializers import UserSerializer


class AuditLogSerializer(serializers.ModelSerializer):
    performed_by = UserSerializer(read_only=True)
    leave_request_id = serializers.IntegerField(source='leave_request.id', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)

    class Meta:
        model = AuditLog
        fields = ['id', 'leave_request_id', 'action', 'action_display', 
                 'performed_by', 'performed_at', 'comments']
        read_only_fields = ['performed_at']