from django.contrib import admin
from django.contrib.auth.models import User

from .models import Student, Attendance


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'roll_number',
        'registration_number',
        'email',
        'branch',
        'semester',
        'login_account',
    )

    search_fields = (
        'name',
        'roll_number',
        'registration_number',
        'email',
    )

    list_filter = (
        'branch',
        'semester',
    )

    actions = [
        'create_student_accounts',
    ]

    @admin.display(
        boolean=True,
        description='Login Account'
    )
    def login_account(self, obj):

        return obj.user is not None

    @admin.action(
        description='Create login accounts for selected students'
    )
    def create_student_accounts(self, request, queryset):

        created_count = 0

        for student in queryset:

            if student.user is not None:
                continue

            username = student.roll_number

            if User.objects.filter(
                username=username
            ).exists():
                continue

            user = User.objects.create_user(
                username=username,
                email=student.email,
                password=student.roll_number,
                first_name=student.name
            )

            student.user = user
            student.save()

            created_count += 1

        self.message_user(
            request,
            f'{created_count} student login account(s) created successfully.'
        )


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'date',
        'status',
    )

    search_fields = (
        'student__name',
        'student__roll_number',
    )

    list_filter = (
        'date',
        'status',
    )