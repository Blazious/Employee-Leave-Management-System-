from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing audit logs.
    
    list:
    Return a list of all audit logs.
    
    retrieve:
    Return the specified audit log.
    """
    queryset = AuditLog.objects.select_related('leave_request', 'performed_by').all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['leave_request', 'action', 'performed_by']
    search_fields = ['comments', 'action']
    ordering_fields = ['performed_at', 'action']
    ordering = ['-performed_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        # If user is not staff, only show audit logs for their leave requests
        if not self.request.user.is_staff:
            queryset = queryset.filter(leave_request__employee=self.request.user)
        return queryset
