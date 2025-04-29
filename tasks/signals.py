from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Task, Notification


from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=Task)
def task_notification(sender, instance, created, **kwargs):
    """Send email notification ONLY to the assigned employee(s)."""

    print("✅ Task Notification Signal Triggered")

    subject = "New Task Notification"
    message = f"Task '{instance.title}' has been assigned or updated.\n\nDescription: {instance.description}\nStatus: {instance.status}\nDue Date: {instance.due_date}"

    # ✅ FIX: Get only the assigned employee(s) emails
    assigned_employees = instance.assigned_to.all()
    recipient_list = [emp.user.email for emp in assigned_employees if emp.user.email]

    print(f"👀 Assigned Users: {assigned_employees}")
    print(f"📨 Email Recipients (Assigned Employees): {recipient_list}")

    # Create an in-app notification for assigned employees
    for employee in assigned_employees:
        Notification.objects.create(user=employee.user, message=message)
        print(f"📩 Notification Created for: {employee.user.email}")

    if recipient_list:
        print("📤 Sending Email to Assigned Employees...")
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            recipient_list,
            fail_silently=False
        )
        print("✅ Email Sent Successfully!")
    else:
        print("⚠️ No Email Sent: No assigned employees found or no emails set.")
