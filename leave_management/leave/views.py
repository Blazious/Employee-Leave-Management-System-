from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import LeaveType, LeaveRequest, LeaveBalance
from .serializers import LeaveTypeSerializer, LeaveRequestSerializer, LeaveBalanceSerializer
from .utils import generate_leave_pdf  # Your PDF generation function

# Custom permission for workflow
class IsHODOrHR(permissions.BasePermission):
    """Allow HOD to approve pending leave, HR to finalize approvals"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["HOD", "HR"]

class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [permissions.IsAuthenticated]  # All authenticated users can view


class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all().order_by("-applied_at")
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsHODOrHR])
    def approve(self, request, pk=None):
        leave = self.get_object()
        approver = request.user
        comments = request.data.get("comments", "")
        if leave.status != LeaveRequest.STATUS_PENDING:
            return Response({"detail": "Leave already processed."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Approval workflow
        if approver.role == "HOD":
            leave.status = LeaveRequest.STATUS_PENDING  # HR finalizes later
        elif approver.role == "HR":
            leave.status = LeaveRequest.STATUS_APPROVED
        leave.approved_by = approver
        leave.comments = comments
        leave.save()
        return Response({"detail": f"Leave approved by {approver.role}."})

    @action(detail=True, methods=["post"], permission_classes=[IsHODOrHR])
    def reject(self, request, pk=None):
        leave = self.get_object()
        approver = request.user
        comments = request.data.get("comments", "")
        leave.status = LeaveRequest.STATUS_REJECTED
        leave.approved_by = approver
        leave.comments = comments
        leave.save()
        return Response({"detail": f"Leave rejected by {approver.role}."})

    @action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def download_pdf(self, request, pk=None):
        leave = self.get_object()
        pdf_file = generate_leave_pdf(leave)  # utils.py should return a BytesIO object
        response = Response(pdf_file.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Leave_{leave.id}.pdf"'
        return response


class LeaveBalanceViewSet(viewsets.ModelViewSet):
    queryset = LeaveBalance.objects.all()
    serializer_class = LeaveBalanceSerializer
    permission_classes = [permissions.IsAuthenticated]
