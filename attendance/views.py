from io import BytesIO

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from .models import Student, Attendance


def home(request):
    return render(request, 'attendance/home.html')


def login_view(request):
    if request.user.is_authenticated:

        if hasattr(request.user, 'student'):
            return redirect('student_dashboard')

        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)

            if hasattr(user, 'student'):
                return redirect('student_dashboard')

            return redirect('dashboard')

        return render(
            request,
            'attendance/login.html',
            {'error': 'Invalid username or password.'}
        )

    return render(request, 'attendance/login.html')


@login_required(login_url='login')
def dashboard(request):

    if hasattr(request.user, 'student'):
        return redirect('student_dashboard')

    total_students = Student.objects.count()
    today = timezone.localdate()

    return render(
        request,
        'attendance/dashboard.html',
        {
            'total_students': total_students,
            'today': today,
        }
    )


@login_required(login_url='login')
def student_dashboard(request):

    if not hasattr(request.user, 'student'):
        return redirect('dashboard')

    student = request.user.student

    attendance_records = Attendance.objects.filter(
        student=student
    ).order_by('-date')

    total_classes = attendance_records.count()

    present_classes = attendance_records.filter(
        status=True
    ).count()

    absent_classes = attendance_records.filter(
        status=False
    ).count()

    if total_classes > 0:
        attendance_percentage = (
            present_classes / total_classes
        ) * 100
    else:
        attendance_percentage = 0

    required_classes = 0

    if attendance_percentage < 75 and total_classes > 0:

        while (
            (present_classes + required_classes)
            / (total_classes + required_classes)
        ) < 0.75:

            required_classes += 1

    return render(
        request,
        'attendance/student_dashboard.html',
        {
            'student': student,
            'attendance_records': attendance_records,
            'total_classes': total_classes,
            'present_classes': present_classes,
            'absent_classes': absent_classes,
            'attendance_percentage': attendance_percentage,
            'required_classes': required_classes,
        }
    )


@login_required(login_url='login')
def student_list(request):

    if hasattr(request.user, 'student'):
        return redirect('student_dashboard')

    students = Student.objects.all()

    return render(
        request,
        'attendance/student_list.html',
        {
            'students': students
        }
    )


@login_required(login_url='login')
def add_student(request):

    if hasattr(request.user, 'student'):
        return redirect('student_dashboard')

    if request.method == 'POST':

        name = request.POST.get('name')
        roll_number = request.POST.get('roll_number')
        registration_number = request.POST.get(
            'registration_number'
        )
        email = request.POST.get('email')
        branch = request.POST.get('branch')
        semester = request.POST.get('semester')

        Student.objects.create(
            name=name,
            roll_number=roll_number,
            registration_number=registration_number,
            email=email,
            branch=branch,
            semester=semester
        )

        return redirect('student_list')

    return render(
        request,
        'attendance/add_student.html'
    )


@login_required(login_url='login')
def bulk_import(request):

    if hasattr(request.user, 'student'):
        return redirect('student_dashboard')

    if request.method == 'POST':

        student_data = request.POST.get(
            'student_data',
            ''
        )

        lines = student_data.splitlines()

        imported_count = 0
        skipped_count = 0

        for line in lines:

            line = line.strip()

            if not line:
                continue

            if line.isdigit():
                continue

            if '/' in line and ':' in line:
                continue

            parts = line.split()

            email = None
            email_index = None

            for index, part in enumerate(parts):

                if '@' in part:
                    email = part.strip()
                    email_index = index
                    break

            if not email:
                continue

            name = ' '.join(
                parts[:email_index]
            ).strip()

            remaining = parts[email_index + 1:]

            roll_number = None

            if remaining:
                roll_number = remaining[-1].strip()

            if not name:
                skipped_count += 1
                continue

            if Student.objects.filter(
                email=email
            ).exists():
                skipped_count += 1
                continue

            if roll_number:

                if Student.objects.filter(
                    roll_number=roll_number
                ).exists():

                    skipped_count += 1
                    continue

            if not roll_number:
                roll_number = (
                    f'TEMP-{imported_count + 1}'
                )

            Student.objects.create(
                name=name,
                roll_number=roll_number,
                registration_number=roll_number,
                email=email,
                branch='CSE',
                semester=5
            )

            imported_count += 1

        return render(
            request,
            'attendance/bulk_import.html',
            {
                'imported_count': imported_count,
                'skipped_count': skipped_count,
                'import_completed': True,
            }
        )

    return render(
        request,
        'attendance/bulk_import.html'
    )


@login_required(login_url='login')
def delete_student(request, student_id):

    if hasattr(request.user, 'student'):
        return redirect('student_dashboard')

    if request.method == 'POST':

        student = get_object_or_404(
            Student,
            id=student_id
        )

        student.delete()

    return redirect('student_list')


@login_required(login_url='login')
def mark_attendance(request):

    if hasattr(request.user, 'student'):
        return redirect('student_dashboard')

    students = Student.objects.all()

    if request.method == 'POST':

        attendance_date = request.POST.get('date')

        for student in students:

            status = request.POST.get(
                f'student_{student.id}'
            )

            is_present = status == 'present'

            Attendance.objects.update_or_create(
                student=student,
                date=attendance_date,
                defaults={
                    'status': is_present
                }
            )

        messages.success(
            request,
            'Attendance saved successfully!'
        )

        return redirect(
            f'/attendance/?date={attendance_date}'
        )

    selected_date = request.GET.get('date')

    existing_attendance = {}

    if selected_date:

        attendance_records = Attendance.objects.filter(
            date=selected_date
        )

        for record in attendance_records:

            existing_attendance[
                record.student.id
            ] = record.status

    for student in students:

        student.attendance_status = (
            existing_attendance.get(
                student.id
            )
        )

    return render(
        request,
        'attendance/mark_attendance.html',
        {
            'students': students,
            'selected_date': selected_date,
        }
    )


@login_required(login_url='login')
def attendance_report(request):

    if hasattr(request.user, 'student'):
        return redirect('student_dashboard')

    students = Student.objects.all()

    for student in students:

        attendance_records = Attendance.objects.filter(
            student=student
        )

        total_classes = attendance_records.count()

        present_classes = attendance_records.filter(
            status=True
        ).count()

        if total_classes > 0:

            attendance_percentage = (
                present_classes / total_classes
            ) * 100

        else:

            attendance_percentage = 0

        student.total_classes = total_classes

        student.present_classes = present_classes

        student.attendance_percentage = (
            attendance_percentage
        )

        if (
            attendance_percentage < 75
            and total_classes > 0
        ):

            required_classes = 0

            while (
                (present_classes + required_classes)
                / (total_classes + required_classes)
            ) < 0.75:

                required_classes += 1

            student.required_classes = (
                required_classes
            )

        else:

            student.required_classes = 0

    return render(
        request,
        'attendance/attendance_report.html',
        {
            'students': students,
        }
    )


def build_student_pdf(student):
    attendance_records = Attendance.objects.filter(
        student=student
    ).order_by('-date')

    total_classes = attendance_records.count()

    present_classes = attendance_records.filter(
        status=True
    ).count()

    absent_classes = total_classes - present_classes

    if total_classes > 0:
        attendance_percentage = (
            present_classes / total_classes
        ) * 100
    else:
        attendance_percentage = 0

    if attendance_percentage >= 75:
        status = 'Above 75%'

    elif total_classes == 0:
        status = 'No attendance'

    else:
        required_classes = 0

        while (
            (present_classes + required_classes)
            / (total_classes + required_classes)
        ) < 0.75:

            required_classes += 1

        status = (
            f'Attend next {required_classes} classes'
        )

    pdf_buffer = BytesIO()

    document = SimpleDocTemplate(
        pdf_buffer,
        pagesize=landscape(A4),
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'StudentReportTitle',
        parent=styles['Title'],
        alignment=TA_CENTER,
        fontSize=20,
        leading=24,
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        'StudentReportSubtitle',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontSize=10,
        leading=14,
        spaceAfter=10
    )

    story = []

    story.append(
        Paragraph(
            'AttendEase',
            title_style
        )
    )

    story.append(
        Paragraph(
            'Individual Student Attendance Report',
            subtitle_style
        )
    )

    story.append(
        Paragraph(
            f'Student: {student.name}',
            subtitle_style
        )
    )

    story.append(
        Paragraph(
            f'Roll Number: {student.roll_number}',
            subtitle_style
        )
    )

    story.append(
        Paragraph(
            f'Generated on {timezone.localdate().strftime("%d %B %Y")}',
            subtitle_style
        )
    )

    table_data = [
        [
            'Date',
            'Status'
        ]
    ]

    for record in attendance_records:

        record_status = 'Present' if record.status else 'Absent'

        table_data.append(
            [
                record.date.strftime('%d %B %Y'),
                record_status
            ]
        )

    if len(table_data) == 1:
        table_data.append(
            [
                'No attendance records',
                '-'
            ]
        )

    table = Table(
        table_data,
        repeatRows=1,
        colWidths=[
            90 * mm,
            50 * mm
        ]
    )

    table.setStyle(
        TableStyle(
            [
                (
                    'BACKGROUND',
                    (0, 0),
                    (-1, 0),
                    colors.HexColor('#b71c1c')
                ),
                (
                    'TEXTCOLOR',
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    'FONTNAME',
                    (0, 0),
                    (-1, 0),
                    'Helvetica-Bold'
                ),
                (
                    'ALIGN',
                    (0, 0),
                    (-1, -1),
                    'CENTER'
                ),
                (
                    'VALIGN',
                    (0, 0),
                    (-1, -1),
                    'MIDDLE'
                ),
                (
                    'GRID',
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    'ROWBACKGROUNDS',
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor('#f7f7f7')
                    ]
                ),
                (
                    'FONTSIZE',
                    (0, 0),
                    (-1, -1),
                    9
                ),
                (
                    'TOPPADDING',
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    'BOTTOMPADDING',
                    (0, 0),
                    (-1, -1),
                    7
                )
            ]
        )
    )

    story.append(table)

    story.append(
        Spacer(1, 15)
    )

    summary_data = [
        ['Total Classes', total_classes],
        ['Present Classes', present_classes],
        ['Absent Classes', absent_classes],
        ['Attendance Percentage', f'{attendance_percentage:.1f}%'],
        ['75% Status', status],
    ]

    summary_table = Table(
        summary_data,
        colWidths=[
            60 * mm,
            100 * mm
        ]
    )

    summary_table.setStyle(
        TableStyle(
            [
                (
                    'GRID',
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    'FONTNAME',
                    (0, 0),
                    (0, -1),
                    'Helvetica-Bold'
                ),
                (
                    'ALIGN',
                    (1, 0),
                    (1, -1),
                    'CENTER'
                ),
                (
                    'FONTSIZE',
                    (0, 0),
                    (-1, -1),
                    9
                ),
                (
                    'TOPPADDING',
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    'BOTTOMPADDING',
                    (0, 0),
                    (-1, -1),
                    7
                )
            ]
        )
    )

    story.append(summary_table)

    story.append(
        Spacer(1, 12)
    )

    story.append(
        Paragraph(
            'AttendEase Attendance Management System',
            subtitle_style
        )
    )

    document.build(story)

    pdf_buffer.seek(0)

    return pdf_buffer


@login_required(login_url='login')
def attendance_pdf(request):

    if hasattr(request.user, 'student'):
        return redirect('student_dashboard')

    students = Student.objects.all().order_by(
        'roll_number'
    )

    response = HttpResponse(
        content_type='application/pdf'
    )

    response[
        'Content-Disposition'
    ] = 'attachment; filename="AttendEase_Attendance_Report.pdf"'

    document = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        rightMargin=12 * mm,
        leftMargin=12 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Title'],
        alignment=TA_CENTER,
        fontSize=20,
        leading=24,
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        'ReportSubtitle',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontSize=10,
        leading=14,
        spaceAfter=15
    )

    story = []

    story.append(
        Paragraph(
            'AttendEase',
            title_style
        )
    )

    story.append(
        Paragraph(
            'Student Attendance Report',
            subtitle_style
        )
    )

    story.append(
        Paragraph(
            f'Generated on {timezone.localdate().strftime("%d %B %Y")}',
            subtitle_style
        )
    )

    table_data = [
        [
            'Name',
            'Roll Number',
            'Total Classes',
            'Present',
            'Absent',
            'Attendance %',
            '75% Status'
        ]
    ]

    for student in students:

        attendance_records = Attendance.objects.filter(
            student=student
        )

        total_classes = attendance_records.count()

        present_classes = attendance_records.filter(
            status=True
        ).count()

        absent_classes = total_classes - present_classes

        if total_classes > 0:

            attendance_percentage = (
                present_classes / total_classes
            ) * 100

        else:

            attendance_percentage = 0

        if attendance_percentage >= 75:

            status = 'Above 75%'

        elif total_classes == 0:

            status = 'No attendance'

        else:

            required_classes = 0

            while (
                (present_classes + required_classes)
                / (total_classes + required_classes)
            ) < 0.75:

                required_classes += 1

            status = (
                f'Attend next {required_classes} classes'
            )

        table_data.append(
            [
                student.name,
                student.roll_number,
                total_classes,
                present_classes,
                absent_classes,
                f'{attendance_percentage:.1f}%',
                status
            ]
        )

    table = Table(
        table_data,
        repeatRows=1,
        colWidths=[
            48 * mm,
            30 * mm,
            28 * mm,
            24 * mm,
            24 * mm,
            30 * mm,
            52 * mm
        ]
    )

    table.setStyle(
        TableStyle(
            [
                (
                    'BACKGROUND',
                    (0, 0),
                    (-1, 0),
                    colors.HexColor('#b71c1c')
                ),
                (
                    'TEXTCOLOR',
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    'FONTNAME',
                    (0, 0),
                    (-1, 0),
                    'Helvetica-Bold'
                ),
                (
                    'ALIGN',
                    (1, 0),
                    (-1, -1),
                    'CENTER'
                ),
                (
                    'VALIGN',
                    (0, 0),
                    (-1, -1),
                    'MIDDLE'
                ),
                (
                    'GRID',
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    'FONTNAME',
                    (0, 1),
                    (-1, -1),
                    'Helvetica'
                ),
                (
                    'FONTSIZE',
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    'ROWBACKGROUNDS',
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor('#f7f7f7')
                    ]
                ),
                (
                    'TOPPADDING',
                    (0, 0),
                    (-1, -1),
                    7
                ),
                (
                    'BOTTOMPADDING',
                    (0, 0),
                    (-1, -1),
                    7
                )
            ]
        )
    )

    story.append(table)

    story.append(
        Spacer(1, 12)
    )

    story.append(
        Paragraph(
            'AttendEase Attendance Management System',
            subtitle_style
        )
    )

    document.build(story)

    return response


@login_required(login_url='login')
def email_student_report(request, student_id):

    if hasattr(request.user, 'student'):
        return redirect('student_dashboard')

    if request.method != 'POST':
        return redirect('attendance_report')

    student = get_object_or_404(
        Student,
        id=student_id
    )

    if not student.email:
        messages.error(
            request,
            f'{student.name} does not have an email address.'
        )

        return redirect('attendance_report')

    pdf_buffer = build_student_pdf(student)

    email = EmailMessage(
        subject=f'AttendEase Attendance Report - {student.name}',
        body=(
            f'Dear {student.name},\n\n'
            'Please find your latest attendance report attached.\n\n'
            'Regards,\n'
            'AttendEase Attendance Management System'
        ),
        from_email=None,
        to=[student.email],
    )

    email.attach(
        f'AttendEase_{student.roll_number}_Attendance_Report.pdf',
        pdf_buffer.getvalue(),
        'application/pdf'
    )

    try:
        email.send(fail_silently=False)

        messages.success(
            request,
            f'Attendance report sent successfully to {student.email}.'
        )

    except Exception:
        messages.error(
            request,
            'The email could not be sent. Please check your email configuration.'
        )

    return redirect('attendance_report')


def logout_view(request):

    if request.method == 'POST':
        logout(request)

    return redirect('home')