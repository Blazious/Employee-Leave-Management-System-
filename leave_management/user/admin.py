from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Department


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Employee Details", {"fields": ("employee_id", "role", "department")}),
    )
    readonly_fields = ("employee_id",)
    list_display = ("employee_id", "username", "email", "role", "department", "is_active")
    list_filter = ("role", "department")


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    readonly_fields = ("department_id",)
    list_display = ("department_id", "name", "description")
    search_fields = ("department_id", "name")
