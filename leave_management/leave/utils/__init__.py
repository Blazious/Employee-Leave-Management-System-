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
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
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
    """Send email notification for leave request status update with PDF attachment"""
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
    
    html_message = render_to_string('email/leave_status_update.html', context)
    plain_message = strip_tags(html_message)
    
    # Create email with PDF attachment
    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[leave_request.employee.email]
    )
    
    # Attach HTML version
    email.attach_alternative(html_message, "text/html")
    
    # Generate and attach PDF only for APPROVED status
    if status.upper() == "APPROVED":
        try:
            pdf_buffer = generate_leave_pdf(leave_request)
            email.attach(
                filename=f"Leave_Request_{leave_request.id}.pdf",
                content=pdf_buffer.getvalue(),
                mimetype="application/pdf"
            )
        except Exception as e:
            # If PDF generation fails, still send the email without attachment
            print(f"Failed to generate PDF for leave request {leave_request.id}: {e}")
    
    email.send(fail_silently=True)

def generate_leave_pdf(leave_request):
    """Generate professional PDF document for leave request"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                           rightMargin=72, leftMargin=72, 
                           topMargin=72, bottomMargin=72)
    styles = getSampleStyleSheet()
    story = []

    # Company Header
    company_style = ParagraphStyle(
        'CompanyHeader',
        parent=styles['Normal'],
        fontSize=18,
        textColor=colors.darkblue,
        alignment=1,  # Center alignment
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )
    
    story.append(Paragraph("ENTERPRISE LEAVE MANAGEMENT SYSTEM", company_style))
    
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.darkgrey,
        alignment=1,
        spaceAfter=20,
        fontName='Helvetica'
    )
    story.append(Paragraph("Official Leave Request Document", subtitle_style))
    
    # Add a decorative line
    from reportlab.platypus import HRFlowable
    story.append(HRFlowable(width="100%", thickness=2, lineCap='round', color=colors.darkblue))
    story.append(Spacer(1, 20))

    # Document Info Header
    doc_info_style = ParagraphStyle(
        'DocInfo',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        alignment=0,
        spaceAfter=15,
        fontName='Helvetica'
    )
    story.append(Paragraph(f"<b>Document ID:</b> LR-{leave_request.id:06d} | <b>Generated:</b> {leave_request.applied_at.strftime('%B %d, %Y at %I:%M %p')}", doc_info_style))

    # Main Title
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor=colors.darkblue,
        alignment=1,
        spaceAfter=30,
        fontName='Helvetica-Bold'
    )
    story.append(Paragraph("LEAVE REQUEST AUTHORIZATION", title_style))
    story.append(Spacer(1, 20))

    # Employee Information Section
    section_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.darkblue,
        spaceAfter=10,
        fontName='Helvetica-Bold',
        leftIndent=0
    )
    story.append(Paragraph("EMPLOYEE INFORMATION", section_style))

    # Employee details with enhanced styling
    employee_data = [
        ["Employee Name:", f"{leave_request.employee.get_full_name()}", "Employee ID:", f"{leave_request.employee.employee_id}"],
        ["Department:", f"{leave_request.employee.department}", "Position:", f"{getattr(leave_request.employee, 'position', 'N/A')}"],
        ["Email:", f"{leave_request.employee.email}", "Phone:", f"{getattr(leave_request.employee, 'phone', 'N/A')}"],
    ]

    employee_table = Table(employee_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 2.5*inch])
    employee_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('BACKGROUND', (0, 0), (0, -1), colors.darkblue),
        ('BACKGROUND', (2, 0), (2, -1), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('TEXTCOLOR', (2, 0), (2, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(employee_table)
    story.append(Spacer(1, 20))

    # Leave Details Section
    story.append(Paragraph("LEAVE REQUEST DETAILS", section_style))

    leave_data = [
        ["Leave Type:", f"{leave_request.leave_type}", "Status:", f"<b>{leave_request.get_status_display()}</b>"],
        ["Start Date:", f"{leave_request.start_date.strftime('%B %d, %Y')}", "End Date:", f"{leave_request.end_date.strftime('%B %d, %Y')}"],
        ["Total Working Days:", f"<b>{calculate_leave_days(leave_request.start_date, leave_request.end_date)} days</b>", "Applied On:", f"{leave_request.applied_at.strftime('%B %d, %Y')}"],
    ]

    leave_table = Table(leave_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 2.5*inch])
    leave_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('BACKGROUND', (0, 0), (0, -1), colors.darkblue),
        ('BACKGROUND', (2, 0), (2, -1), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('TEXTCOLOR', (2, 0), (2, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 12),
        ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(leave_table)
    story.append(Spacer(1, 20))

    # Reason Section
    story.append(Paragraph("REASON FOR LEAVE", section_style))
    reason_style = ParagraphStyle(
        'Reason',
        parent=styles['Normal'],
        fontSize=11,
        leftIndent=20,
        spaceAfter=15,
        fontName='Helvetica',
        borderWidth=1,
        borderColor=colors.grey,
        borderPadding=10,
        backColor=colors.whitesmoke
    )
    story.append(Paragraph(leave_request.reason, reason_style))

    # Approval Information (if applicable)
    if leave_request.approved_by or leave_request.comments:
        story.append(Spacer(1, 15))
        story.append(Paragraph("APPROVAL INFORMATION", section_style))
        
        approval_data = []
        if leave_request.approved_by:
            approval_data.append(["Approved By:", f"{leave_request.approved_by.get_full_name()}"])
            approval_data.append(["Approver Role:", f"{getattr(leave_request.approved_by, 'role', 'N/A')}"])
            approval_data.append(["Approved On:", f"{leave_request.updated_at.strftime('%B %d, %Y at %I:%M %p')}"])
        
        if leave_request.comments:
            approval_data.append(["Comments:", leave_request.comments])
        
        if approval_data:
            approval_table = Table(approval_data, colWidths=[2*inch, 4*inch])
            approval_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
                ('BACKGROUND', (0, 0), (0, -1), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 12),
                ('RIGHTPADDING', (0, 0), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(approval_table)

    # Privacy and Legal Section
    story.append(Spacer(1, 30))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    story.append(Spacer(1, 15))
    
    privacy_style = ParagraphStyle(
        'Privacy',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=0,
        fontName='Helvetica',
        leftIndent=0,
        rightIndent=0
    )
    
    privacy_text = """
    <b>PRIVACY NOTICE:</b> This document contains confidential employee information and is intended solely for authorized personnel. 
    Unauthorized disclosure, distribution, or use of this information is strictly prohibited.<br/><br/>
    
    <b>LEGAL DISCLAIMER:</b> This leave request is subject to company policies and applicable labor laws. 
    Approval is at the discretion of management and may be subject to operational requirements.<br/><br/>
    
    <b>DOCUMENT AUTHENTICITY:</b> This is a computer-generated document. No signature is required for digital authenticity.
    """
    
    story.append(Paragraph(privacy_text, privacy_style))
    
    # Footer
    story.append(Spacer(1, 20))
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.darkblue,
        alignment=1,
        fontName='Helvetica-Bold'
    )
    story.append(Paragraph("Enterprise Leave Management System - Automated Document", footer_style))
    story.append(Paragraph(f"Generated on {leave_request.applied_at.strftime('%B %d, %Y at %I:%M %p')} | Document ID: LR-{leave_request.id:06d}", privacy_style))

    # Build and return the PDF
    doc.build(story)
    buffer.seek(0)
    return buffer