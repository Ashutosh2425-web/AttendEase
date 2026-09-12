"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from attendance.views import (
    home,
    login_view,
    dashboard,
    student_dashboard,
    student_list,
    add_student,
    bulk_import,
    delete_student,
    mark_attendance,
    attendance_report,
    attendance_pdf,
    email_student_report,
    logout_view,
)


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', home, name='home'),

    path('login/', login_view, name='login'),

    path('dashboard/', dashboard, name='dashboard'),

    path(
        'student-dashboard/',
        student_dashboard,
        name='student_dashboard'
    ),

    path('students/', student_list, name='student_list'),

    path(
        'students/add/',
        add_student,
        name='add_student'
    ),

    path(
        'students/import/',
        bulk_import,
        name='bulk_import'
    ),

    path(
        'students/delete/<int:student_id>/',
        delete_student,
        name='delete_student'
    ),

    path(
        'attendance/',
        mark_attendance,
        name='mark_attendance'
    ),

    path(
        'attendance/report/',
        attendance_report,
        name='attendance_report'
    ),

    path(
        'attendance/report/pdf/',
        attendance_pdf,
        name='attendance_pdf'
    ),

    path(
        'attendance/report/email/<int:student_id>/',
        email_student_report,
        name='email_student_report'
    ),

    path('logout/', logout_view, name='logout'),
]