from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import Employee, Task
from .forms import UserRegisterForm, TaskForm, TaskStatusForm
from django.contrib import messages

# Register Conformation Email Purpose Imports
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from .models import UserProfile
from .forms import UserProfileForm


import random
from django.core.mail import send_mail
from django.utils import timezone
from .models import OTP
from .forms import ForgotPasswordForm, OTPVerificationForm, ResetPasswordForm


@login_required
def edit_profile(request):
    # ✅ Create UserProfile if it doesn't exist
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('edit_profile')
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'tasks/edit_profile.html', {'form': form, 'user_profile': user_profile})


def is_admin(user):
    return user.is_staff  # Admin users (Django default)

def is_employee(user):
    return not user.is_staff  # Normal employees


 # Landing page
def landing(request):
    return render(request, 'tasks/landing.html')


# Register Conformation Email purpose view
def send_welcome_email(user):   
    context = {
        'user': user,
        'site_url': 'http://127.0.0.1:8000/'  # Change to your deployed site URL
    }    
    email_html = render_to_string('emails/welcome_email.html', context)    
    subject = "Welcome to Task Manager"
    email = EmailMultiAlternatives(
        subject=subject,
        body="Thank you for registering with Task Manager.",
        from_email=settings.EMAIL_HOST_USER,
        to=[user.email]
    )
    email.attach_alternative(email_html, "text/html")
    email.send()


# Register User
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            Employee.objects.create(user=user)  # Create Employee Profile
            # Send welcome email
            send_welcome_email(user)
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'tasks/register.html', {'form': form})


# Login User
def user_login(request):
    # Check if user is already authenticated
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in!')
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if fields are blank
        if not username or not password:
            messages.error(request, 'Username and Password are required!')
            return redirect('login')

        # Authenticate User
        user = authenticate(request, username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Your account is inactive. Contact admin.')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'tasks/login.html')


# Logout User
def user_logout(request):
    logout(request)
    return redirect('landing')



# Dashboard - Show Tasks
@login_required
def dashboard(request):
    """ Show tasks based on user role """

    if request.user.is_superuser or (hasattr(request.user, 'employee') and request.user.employee.role == 'Admin'):
        # ✅ Super Admins & Task Admins → See all tasks
        tasks = Task.objects.all()
    else:
        # ✅ Employees → See only assigned tasks
        tasks = Task.objects.filter(assigned_to=request.user.employee)

    # Debugging: Print task assignments
    for task in tasks:
        print(f"Task: {task.title}, Assigned To: {[emp.user.username for emp in task.assigned_to.all()]}")
        
    return render(request, "tasks/dashboard.html", {"tasks": tasks})



def is_task_admin(user):
    """Check if the user is an Employee with Admin role."""
    return hasattr(user, 'employee') and user.employee.role == 'Admin'

@login_required
@user_passes_test(is_task_admin)  # ✅ Only Task Admins can access
def create_task(request):
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.save()
            assigned_employees = form.cleaned_data.get("assigned_to")
            if assigned_employees:
                task.assigned_to.set(assigned_employees)
                task.save()
            messages.success(request, "✅ Task created successfully!")  
            return redirect("dashboard")
    else:
        form = TaskForm()
    return render(request, "tasks/create_task.html", {"form": form})




@login_required
def update_task_status(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    # 🔍 Debugging Information
    print(f"🔍 Task ID: {task.id}, Current Status: {task.status}")
    print(f"👤 Assigned Users: {list(task.assigned_to.all())}")
    print(f"🔑 Logged-in User: {request.user} (ID: {request.user.id})")

    # Ensure either the assigned user OR a Task Admin can update the status
    if not task.assigned_to.filter(user=request.user).exists() and not (hasattr(request.user, 'employee') and request.user.employee.role == 'Admin'):
        print("🚫 Unauthorized attempt by:", request.user)
        return redirect('dashboard')

    if request.method == 'POST':
        form = TaskStatusForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Task status updated successfully!")
            return redirect('dashboard')

    else:
        form = TaskStatusForm(instance=task)

    return render(request, 'tasks/update_task_status.html', {'form': form, 'task': task})


def employee_home(request):
    # Placeholder data - we'll later fetch this from the database
    context = {
        'user': request.user,
        'birthdays': [],   # List of upcoming birthdays
        'holidays': [],    # List of upcoming holidays
        'best_employees': []  # Best employees' list for the scrolling section
    }
    # return render(request, 'employees/employee_dashboard.html', context)
    return render(request, 'employees/home.html', context)



def generate_otp():
    return str(random.randint(100000, 999999))

# Forgot Password View
def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                otp = generate_otp()
                OTP.objects.create(user=user, code=otp)
                send_mail(
                    'Password Reset OTP',
                    f'Your OTP for password reset is: {otp}',
                    'noreply@msiit.in',
                    [email],
                    fail_silently=False,
                )
                request.session['reset_email'] = email
                messages.success(request, 'OTP sent to your email.')
                return redirect('verify_otp')
            except User.DoesNotExist:
                messages.error(request, 'No account found with this email.')
    else:
        form = ForgotPasswordForm()
    return render(request, 'tasks/forgot_password.html', {'form': form})

# OTP Verification View
def verify_otp(request):
    if request.method == 'POST':
        form = OTPVerificationForm(request.POST)
        if form.is_valid():
            email = request.session.get('reset_email')
            otp_code = form.cleaned_data['otp']
            try:
                user = User.objects.get(email=email)
                otp = OTP.objects.get(user=user, code=otp_code)
                if not otp.is_expired():
                    request.session['verified_user'] = user.id
                    otp.delete()
                    messages.success(request, 'OTP verified. Reset your password.')
                    return redirect('reset_password')
                else:
                    otp.delete()
                    messages.error(request, 'OTP expired. Please try again.')
                    return redirect('forgot_password')
            except (User.DoesNotExist, OTP.DoesNotExist):
                messages.error(request, 'Invalid OTP.')
    else:
        form = OTPVerificationForm()
    return render(request, 'tasks/verify_otp.html', {'form': form})

# Reset Password View
def reset_password(request):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']
            if new_password == confirm_password:
                user_id = request.session.get('verified_user')
                user = User.objects.get(id=user_id)
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password reset successful!')
                return redirect('login')
            else:
                messages.error(request, 'Passwords do not match.')
    else:
        form = ResetPasswordForm()
    return render(request, 'tasks/reset_password.html', {'form': form})
