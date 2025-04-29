from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)

    def __str__(self):
        return f"{self.user.username} - OTP: {self.code}"


# Employee Model (Extends Django User)
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(
        max_length=20,
        choices=[('Admin', 'Admin'), ('Employee', 'Employee')],
        default='Employee'
    )

    def __str__(self):
        return self.user.username
    


class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(
        max_length=50,
        choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')]
    )
    due_date = models.DateField()
    assigned_to = models.ManyToManyField(Employee, related_name='tasks')
    status = models.CharField(
        max_length=50,
        choices=[('Pending', 'Pending'), ('In Progress', 'In Progress'), ('Completed', 'Completed')],
        default='Pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title



class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)  # Track if notification is read
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.message[:50]}"


def upload_to(instance, filename):
    """Upload path for profile images"""
    return f"profile_images/{instance.user.username}/{filename}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_image = models.ImageField(upload_to=upload_to, null=True, blank=True, default='default_profile.png')
    mobile_number = models.CharField(max_length=15, null=True, blank=True)
    address = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
