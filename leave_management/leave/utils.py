from datetime import date, timedelta
from calendar import day_name
from typing import List, Tuple
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

def get_kenya_holidays(year: int, debug: bool = False) -> List[Tuple[date, str]]:
    """Get comprehensive list of Kenyan holidays."""
    fixed_holidays = [
        (date(year, 1, 1), "New Year's Day"),
        (date(year, 5, 1), "Labour Day"),
        (date(year, 6, 1), "Madaraka Day"),
        (date(year, 10, 10), "Mazingira Day"),
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

def calculate_leave_days(start_date: date, end_date: date) -> int:
    """Calculate working days between dates."""
    holiday_list = get_kenya_holidays(start_date.year)
    
    if start_date.year != end_date.year:
        holiday_list.extend(get_kenya_holidays(end_date.year))
    
    # Extract just the dates from the holiday tuples
    holiday_dates = [h[0] for h in holiday_list]
    # Create a dict for holiday lookup by date
    holiday_dict = dict(holiday_list)
    
    total_days = 0
    current_day = start_date
    
    while current_day <= end_date:
        is_weekend = current_day.weekday() >= 5
        is_holiday = current_day in holiday_dates
        
        if not is_weekend and not is_holiday:
            total_days += 1
        
        current_day += timedelta(days=1)
    
    return total_days

def generate_leave_pdf(leave_request):
    """Generate PDF document for leave request"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30
    )
    story.append(Paragraph("Leave Request Form", title_style))
    story.append(Spacer(1, 12))

    # Leave details
    data = [
        ["Employee Name:", f"{leave_request.employee.get_full_name()}"],
        ["Department:", f"{leave_request.employee.department}"],
        ["Leave Type:", f"{leave_request.leave_type}"],
        ["Start Date:", f"{leave_request.start_date}"],
        ["End Date:", f"{leave_request.end_date}"],
        ["Total Days:", f"{leave_request.total_days}"],
        ["Status:", f"{leave_request.get_status_display()}"],
        ["Applied On:", f"{leave_request.applied_at.strftime('%Y-%m-%d')}"],
    ]

    if leave_request.approved_by:
        data.append(["Approved By:", f"{leave_request.approved_by.get_full_name()}"])
    if leave_request.comments:
        data.append(["Comments:", f"{leave_request.comments}"])

    # Create the table
    table = Table(data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
    ]))
    story.append(table)

    # Build and return the PDF
    doc.build(story)
    buffer.seek(0)
    return buffer
