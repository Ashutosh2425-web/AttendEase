from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render, get_object_or_404
from django.utils import timezone

from .models import Student, Attendance


def home(request):
    return render(request, 'attendance/home.html')


def login_view(request):
    if request.user.is_authenticated:
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
            return redirect('dashboard')

        return render(
            request,
            'attendance/login.html',
            {'error': 'Invalid username or password.'}
        )

    return render(request, 'attendance/login.html')


@login_required(login_url='login')
def dashboard(request):

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
def student_list(request):
    students = Student.objects.all()

    return render(
        request,
        'attendance/student_list.html',
        {'students': students}
    )


@login_required(login_url='login')
def add_student(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        roll_number = request.POST.get('roll_number')
        registration_number = request.POST.get('registration_number')
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

    return render(request, 'attendance/add_student.html')


@login_required(login_url='login')
def bulk_import(request):

    if request.method == 'POST':

        student_data = request.POST.get('student_data', '')

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

            name = ' '.join(parts[:email_index]).strip()

            remaining = parts[email_index + 1:]

            roll_number = None

            if remaining:
                roll_number = remaining[-1].strip()

            if not name:
                skipped_count += 1
                continue

            if Student.objects.filter(email=email).exists():
                skipped_count += 1
                continue

            if roll_number:
                if Student.objects.filter(
                    roll_number=roll_number
                ).exists():
                    skipped_count += 1
                    continue

            if not roll_number:
                roll_number = f'TEMP-{imported_count + 1}'

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

    return render(request, 'attendance/bulk_import.html')


@login_required(login_url='login')
def delete_student(request, student_id):

    if request.method == 'POST':

        student = get_object_or_404(
            Student,
            id=student_id
        )

        student.delete()

    return redirect('student_list')


@login_required(login_url='login')
def mark_attendance(request):

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
            existing_attendance[record.student.id] = record.status

    for student in students:
        student.attendance_status = existing_attendance.get(
            student.id
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
        student.attendance_percentage = attendance_percentage

        if attendance_percentage < 75 and total_classes > 0:

            required_classes = 0

            while (
                (present_classes + required_classes)
                / (total_classes + required_classes)
            ) < 0.75:

                required_classes += 1

            student.required_classes = required_classes

        else:
            student.required_classes = 0

    return render(
        request,
        'attendance/attendance_report.html',
        {
            'students': students,
        }
    )


def logout_view(request):
    if request.method == 'POST':
        logout(request)

    return redirect('home')