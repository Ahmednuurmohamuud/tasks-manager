from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Employee, Task, Notification, UserProfile


admin.site.register(Notification)  

admin.site.register(Employee)

admin.site.register(UserProfile)

class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'status', 'due_date', 'created_at', 'updated_at')
    list_filter = ('priority', 'status', 'created_at')
    search_fields = ('title', 'description')

admin.site.register(Task, TaskAdmin)
