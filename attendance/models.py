from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=50, unique=True)
    registration_number = models.CharField(max_length=50, unique=True)
    email = models.EmailField()
    branch = models.CharField(max_length=100)
    semester = models.IntegerField()

    def __str__(self):
        return self.name


class Attendance(models.Model):
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE
    )
    date = models.DateField()
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.name} - {self.date}"