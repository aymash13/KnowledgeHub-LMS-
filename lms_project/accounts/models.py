from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserTable(models.Model):
    ROLES = [
        ('ADMIN', 'Admin'),
        ('TEACHER', 'Teacher'),
        ('TA', 'Teaching Assistant'),
        ('STUDENT', 'Student'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLES, default='STUDENT')

    def __str__(self):
        return f"{self.user.username} - {self.role}"