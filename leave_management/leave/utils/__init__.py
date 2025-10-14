from datetime import date, timedelta
from calendar import day_name
from typing import List, Tuple
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from ..models import LeaveBalance, LeaveRequest

def calculate_easter(year: int) -> date:
    """
    Calculate Easter Sunday using the Anonymous Gregorian algorithm.
    This is a more widely tested and reliable algorithm for Easter calculation.
    """
    y = year
    a = y % 19
    b = y // 100
    c = y % 100
    d = b // 4
    e = b % 4
    g = (8 * b + 13) // 25
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    
    return date(y, month, day)

def get_kenya_holidays(year: int, debug: bool = False) -> List[Tuple[date, str]]:
    """Get comprehensive list of Kenyan holidays."""
    fixed_holidays = [
        (date(year, 1, 1), "New Year's Day"),
        (date(year, 5, 1), "Labour Day"),
        (date(year, 6, 1), "Madaraka Day"),
        (date(year, 10, 20), "Mashujaa Day"),
        (date(year, 12, 12), "Jamhuri Day"),
        (date(year, 12, 25), "Christmas Day"),
        (date(year, 12, 26), "Boxing Day")
    ]
    
    # Calculate Easter-based holidays
    easter = calculate_easter(year)
    good_friday = easter - timedelta(days=2)
    easter_monday = easter + timedelta(days=1)
    variable_holidays = [
        (good_friday, "Good Friday"),
        (easter_monday, "Easter Monday")
    ]
    
    # Combine all holidays
    all_holidays = fixed_holidays + variable_holidays
    
    if debug:
        print("\nKenya Public Holidays:")
        print("Fixed Holidays:")
        for holiday_date, holiday_name in fixed_holidays:
            print(f"- {holiday_date.strftime('%d %B %Y')} ({day_name[holiday_date.weekday()]}): {holiday_name}")
        print("\nVariable Religious Holidays:")
        for holiday_date, holiday_name in variable_holidays:
            print(f"- {holiday_date.strftime('%d %B %Y')} ({day_name[holiday_date.weekday()]}): {holiday_name}")
    
    return all_holidays

def calculate_leave_days(start_date: date, end_date: date) -> int:
    """Calculate working days between dates."""
    holiday_list = get_kenya_holidays(start_date.year)
    
    if start_date.year != end_date.year:
        holiday_list.extend(get_kenya_holidays(end_date.year))
    
    # Extract just the dates from the holiday tuples
    holiday_dates = [h[0] for h in holiday_list]
    
    total_days = 0
    current_day = start_date
    
    while current_day <= end_date:
        is_weekend = current_day.weekday() >= 5
        is_holiday = current_day in holiday_dates
        
        if not is_weekend and not is_holiday:
            total_days += 1
        
        current_day += timedelta(days=1)
    
    return total_days

def send_leave_request_email(leave_request):
    """Send email notification for new leave request"""
    subject = f"New Leave Request from {leave_request.employee.get_full_name()}"
    
    context = {
        'employee': leave_request.employee,
        'leave_type': leave_request.leave_type,
        'start_date': leave_request.start_date,
        'end_date': leave_request.end_date,
        'total_days': calculate_leave_days(leave_request.start_date, leave_request.end_date),
        'reason': leave_request.reason
    }
    
    # Get HR and HOD email addresses from settings or use a default
    recipient_list = getattr(settings, 'LEAVE_APPROVAL_EMAILS', ['admin@example.com'])
    
    html_message = render_to_string('leave/email/leave_request.html', context)
    plain_message = render_to_string('leave/email/leave_request.txt', context)
    
    send_mail(
        subject=subject,
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=True
    )

def send_leave_status_update_email(leave_request, status):
    """Send email notification for leave request status update"""
    subject = f"Leave Request {status.title()}"
    
    context = {
        'employee': leave_request.employee,
        'leave_type': leave_request.leave_type,
        'start_date': leave_request.start_date,
        'end_date': leave_request.end_date,
        'total_days': calculate_leave_days(leave_request.start_date, leave_request.end_date),
        'status': status,
        'comments': leave_request.comments,
        'approved_by': leave_request.approved_by
    }
    
    html_message = render_to_string('leave/email/leave_status_update.html', context)
    plain_message = render_to_string('leave/email/leave_status_update.txt', context)
    
    send_mail(
        subject=subject,
        message=plain_message,
        html_message=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[leave_request.employee.email],
        fail_silently=True
    )

def generate_leave_pdf(leave_request):
    """Generate professional PDF document for leave request"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                           topMargin=1*inch, bottomMargin=1*inch,
                           leftMargin=0.75*inch, rightMargin=0.75*inch)
    styles = getSampleStyleSheet()
    story = []

    # Company Header
    company_header_style = ParagraphStyle(
        'CompanyHeader',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.darkblue,
        alignment=1,  # Center alignment
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )
    
    company_address_style = ParagraphStyle(
        'CompanyAddress',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,  # Center alignment
        spaceAfter=30,
        fontName='Helvetica'
    )

    story.append(Paragraph("ENTERPRISE LEAVE MANAGEMENT SYSTEM", company_header_style))
    story.append(Paragraph("Official Leave Request Document", company_address_style))
    story.append(Spacer(1, 20))

    # Document Title
    title_style = ParagraphStyle(
        'DocumentTitle',
        parent=styles['Heading1'],
        fontSize=14,
        textColor=colors.darkblue,
        alignment=1,
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )
    story.append(Paragraph("EMPLOYEE LEAVE REQUEST FORM", title_style))
    story.append(Spacer(1, 15))

    # Compute total working days
    total_days = calculate_leave_days(leave_request.start_date, leave_request.end_date)

    # Employee Information Section
    emp_info_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.darkblue,
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )
    
    story.append(Paragraph("EMPLOYEE INFORMATION", emp_info_style))
    
    # Employee details table
    emp_data = [
        ["Employee ID:", f"{leave_request.employee.employee_id}"],
        ["Full Name:", f"{leave_request.employee.get_full_name()}"],
        ["Department:", f"{leave_request.employee.department.name if leave_request.employee.department else 'N/A'}"],
        ["Department ID:", f"{leave_request.employee.department.department_id if leave_request.employee.department else 'N/A'}"],
        ["Position:", f"{leave_request.employee.role.replace('_', ' ').title()}"],
        ["Email:", f"{leave_request.employee.email}"],
        ["Request Date:", f"{leave_request.applied_at.strftime('%B %d, %Y at %I:%M %p')}"],
    ]

    emp_table = Table(emp_data, colWidths=[2.2*inch, 3.8*inch])
    emp_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(emp_table)
    story.append(Spacer(1, 20))

    # Leave Details Section
    story.append(Paragraph("LEAVE REQUEST DETAILS", emp_info_style))
    
    leave_data = [
        ["Leave Type:", f"{leave_request.leave_type.name}"],
        ["Leave Category:", f"{leave_request.leave_type.description}"],
        ["Start Date:", f"{leave_request.start_date.strftime('%B %d, %Y')} ({leave_request.start_date.strftime('%A')})"],
        ["End Date:", f"{leave_request.end_date.strftime('%B %d, %Y')} ({leave_request.end_date.strftime('%A')})"],
        ["Total Working Days:", f"{total_days} days"],
        ["Reason for Leave:", f"{leave_request.reason}"],
        ["Request Status:", f"{leave_request.get_status_display()}"],
    ]

    if leave_request.approved_by:
        leave_data.append(["Approved By:", f"{leave_request.approved_by.get_full_name()} ({leave_request.approved_by.role})"])
        leave_data.append(["Approval Date:", f"{leave_request.updated_at.strftime('%B %d, %Y at %I:%M %p')}"])
    
    if leave_request.comments:
        leave_data.append(["Manager Comments:", f"{leave_request.comments}"])

    leave_table = Table(leave_data, colWidths=[2.2*inch, 3.8*inch])
    leave_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(leave_table)
    story.append(Spacer(1, 20))

    # Company Policies Section
    story.append(Paragraph("COMPANY LEAVE POLICIES & TERMS", emp_info_style))
    
    policy_text = """
    <b>1. Leave Entitlement:</b> All leave requests are subject to approval based on business requirements and employee entitlement.<br/><br/>
    
    <b>2. Notice Period:</b> Leave requests should be submitted with adequate notice as per company policy (minimum 48 hours for emergency leave).<br/><br/>
    
    <b>3. Documentation:</b> Medical certificates may be required for sick leave exceeding 3 days. Supporting documentation must be provided when requested.<br/><br/>
    
    <b>4. Holiday Periods:</b> Leave during peak business periods may be restricted. Alternative dates may be suggested by management.<br/><br/>
    
    <b>5. Return to Work:</b> Employees must report back to work on the scheduled return date or notify their supervisor immediately of any delays.<br/><br/>
    
    <b>6. Leave Balance:</b> Leave is subject to available balance and cannot exceed annual entitlement without special authorization.<br/><br/>
    
    <b>7. Work Coverage:</b> Employees are responsible for ensuring adequate work coverage during their absence and handing over responsibilities.<br/><br/>
    
    <b>8. Emergency Contact:</b> Employees must provide emergency contact information and remain reachable during leave periods when necessary.
    """
    
    policy_style = ParagraphStyle(
        'PolicyText',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=10,
        fontName='Helvetica',
        leftIndent=20,
        rightIndent=20,
        leading=12
    )
    
    story.append(Paragraph(policy_text, policy_style))
    story.append(Spacer(1, 15))

    # Signatures Section
    signature_style = ParagraphStyle(
        'SignatureHeader',
        parent=styles['Heading3'],
        fontSize=11,
        spaceAfter=15,
        fontName='Helvetica-Bold'
    )
    
    story.append(Paragraph("AUTHORIZATION & SIGNATURES", signature_style))
    
    sig_data = [
        ["Employee Signature:", "_________________________", "Date: _______________"],
        ["Supervisor/Manager:", "_________________________", "Date: _______________"],
        ["HR Department:", "_________________________", "Date: _______________"],
    ]
    
    sig_table = Table(sig_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('LINEBELOW', (1, 0), (1, -1), 1, colors.black),
        ('LINEBELOW', (2, 0), (2, -1), 1, colors.black),
    ]))
    story.append(sig_table)
    story.append(Spacer(1, 25))

    # Privacy Statement
    privacy_style = ParagraphStyle(
        'PrivacyText',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=1,  # Center alignment
        spaceAfter=10,
        fontName='Helvetica',
        leading=10
    )
    
    privacy_text = """
    <b>PRIVACY STATEMENT & DATA PROTECTION NOTICE</b><br/><br/>
    
    This document contains confidential employee information and is protected under the company's privacy policy. 
    The information contained herein is for official business purposes only and may not be disclosed to unauthorized parties. 
    By processing this leave request, the company confirms compliance with applicable data protection regulations and 
    maintains appropriate safeguards for personal information.<br/><br/>
    
    <i>Document generated electronically by the Enterprise Leave Management System on {}</i><br/>
    <i>System Reference: LR-{}-{}</i>
    """.format(
        leave_request.applied_at.strftime('%B %d, %Y'),
        leave_request.employee.employee_id,
        leave_request.id
    )
    
    story.append(Paragraph(privacy_text, privacy_style))

    # Build and return the PDF
    doc.build(story)
    buffer.seek(0)
    return buffer