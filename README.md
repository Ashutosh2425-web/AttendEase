# AttendEase

AttendEase is a web-based Attendance Management System developed using Django. It provides a simple and professional platform for teachers to manage student records, mark attendance, generate attendance reports, and send individual attendance reports through email.

## Live Demo

https://attendease-a0fa.onrender.com

## GitHub Repository

https://github.com/Ashutosh2425-web/AttendEase

## Features

- Teacher/Admin authentication
- Student login
- Student management
- Add new students
- Delete student records
- Bulk student import
- Automatic student login account creation
- Mark daily attendance
- View attendance reports
- Calculate attendance percentage
- Student attendance dashboard
- Generate attendance reports as PDF
- Send individual attendance reports through email
- Professional university-style user interface
- Responsive dashboard design

## Technologies Used

- Python
- Django
- SQLite
- HTML5
- CSS3
- JavaScript
- Bootstrap
- ReportLab
- SMTP / Gmail
- Gunicorn
- WhiteNoise
- Git and GitHub
- Render

## Project Structure

```text
AttendEase/
│
├── attendance/
│   ├── migrations/
│   ├── management/
│   │   └── commands/
│   ├── static/
│   │   └── attendance/
│   ├── templates/
│   │   └── attendance/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
