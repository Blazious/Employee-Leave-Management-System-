from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse, HttpResponse
from datetime import date
from .models import LeaveType, LeaveRequest, LeaveBalance
from .serializers import LeaveTypeSerializer, LeaveRequestSerializer, LeaveBalanceSerializer
from .utils import get_kenya_holidays, calculate_leave_days, generate_leave_pdf, send_leave_status_update_email


class IsHODOrHR(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ["HOD", "HR"]


class LeaveTypeViewSet(viewsets.ModelViewSet):
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    permission_classes = [permissions.IsAuthenticated]


class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all().order_by("-applied_at")
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        leave_request = serializer.save(employee=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsHODOrHR])
    def approve(self, request, pk=None):
        leave = self.get_object()
        approver = request.user
        comments = request.data.get("comments", "")
        if leave.status != LeaveRequest.STATUS_PENDING:
            return Response({"detail": "Leave already processed."}, status=status.HTTP_400_BAD_REQUEST)
        
        if approver.role == "HOD":
            leave.status = LeaveRequest.STATUS_PENDING
        elif approver.role == "HR":
            leave.status = LeaveRequest.STATUS_APPROVED
            # Send email notification with PDF attachment when approved by HR
            send_leave_status_update_email(leave, "APPROVED")
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
        # Send email notification for rejection
        send_leave_status_update_email(leave, "REJECTED")
        return Response({"detail": f"Leave rejected by {approver.role}."})

    @action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def download_pdf(self, request, pk=None):
        leave = self.get_object()
        pdf_buffer = generate_leave_pdf(leave)
        pdf_bytes = pdf_buffer.getvalue()
        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f"attachment; filename=Leave_{leave.id}.pdf"
        response["Content-Length"] = str(len(pdf_bytes))
        return response


class LeaveBalanceViewSet(viewsets.ModelViewSet):
    queryset = LeaveBalance.objects.all()
    serializer_class = LeaveBalanceSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_holiday_calculation(request):
    """Test endpoint for holiday calculations"""
    year = date.today().year
    holidays = get_kenya_holidays(year, debug=True)
    
    start_date = date(year, 10, 10)
    end_date = date(year, 10, 23)
    total_days = calculate_leave_days(start_date, end_date)
    
    holiday_list = []
    for holiday_date, holiday_name in holidays:
        holiday_list.append({
            'date': str(holiday_date),
            'name': holiday_name,
            'day': holiday_date.strftime('%A')
        })
    
    return JsonResponse({
        'holidays': holiday_list,
        'calculation': {
            'start_date': str(start_date),
            'end_date': str(end_date),
            'total_working_days': total_days
        }
    })
