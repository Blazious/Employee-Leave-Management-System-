from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags


def send_leave_request_email(leave_request):
    """
    Send email notification to manager about new leave request
    """
    context = {
        'manager_name': leave_request.manager.get_full_name() if leave_request.manager else 'Manager',
        'employee_name': leave_request.employee.get_full_name(),
        'leave_type': leave_request.leave_type,
        'start_date': leave_request.start_date,
        'end_date': leave_request.end_date,
        'total_days': leave_request.total_days,
        'reason': leave_request.reason
    }
    
    html_message = render_to_string('email/leave_request.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject='New Leave Request',
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[leave_request.manager.email] if leave_request.manager else [],
        html_message=html_message
    )

def send_leave_status_update_email(leave_request, status):
    """
    Send email notification to employee about leave request status update
    """
    context = {
        'employee_name': leave_request.employee.get_full_name(),
        'manager_name': leave_request.manager.get_full_name() if leave_request.manager else 'Manager',
        'status': status.upper(),
        'leave_type': leave_request.leave_type,
        'start_date': leave_request.start_date,
        'end_date': leave_request.end_date,
        'total_days': leave_request.total_days,
        'comments': leave_request.manager_comment
    }
    
    html_message = render_to_string('email/leave_status_update.html', context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject=f'Leave Request {status}',
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[leave_request.employee.email],
        html_message=html_message
    )