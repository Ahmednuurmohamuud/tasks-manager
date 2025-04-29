from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),                        
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create-task/', views.create_task, name='create_task'),  # Admin only
    path('task/<int:task_id>/update-status/', views.update_task_status, name='update_task_status'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('employee_home/', views.employee_home, name='employee_home'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
    
]
