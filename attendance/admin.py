from django.contrib import admin
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
    )
    search_fields = (
        'name',
        'roll_number',
        'registration_number',
    )
    list_filter = (
        'branch',
        'semester',
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