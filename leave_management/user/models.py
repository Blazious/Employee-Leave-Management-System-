from django.contrib.auth.models import AbstractUser
from django.db import models


def generate_prefix(name: str) -> str:
    """Generate a 3-letter uppercase prefix from department name."""
    return name.strip().upper()[:3]  # e.g. Finance -> FIN, Operations -> OPE


class Department(models.Model):
    department_id = models.CharField(max_length=10, unique=True, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def save(self, *args, **kwargs):
        if not self.department_id:
            prefix = generate_prefix(self.name)
            # Find the last department with the same prefix
            last_dept = Department.objects.filter(
                department_id__startswith=prefix
            ).order_by("-department_id").first()
            if last_dept:
                last_num = int(last_dept.department_id.replace(prefix, ""))
                new_num = last_num + 1
            else:
                new_num = 1
            self.department_id = f"{prefix}{new_num:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.department_id} - {self.name}"


class User(AbstractUser):
    # Role choices
    EMPLOYEE = "EMPLOYEE"
    HOD = "HOD"
    HR = "HR"
    ADMIN = "ADMIN"

    ROLE_CHOICES = [
        (EMPLOYEE, "Employee"),
        (HOD, "Head of Department"),
        (HR, "HR"),
        (ADMIN, "Admin"),
    ]

    employee_id = models.CharField(max_length=10, unique=True, editable=False, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=EMPLOYEE)
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="users"
    )

    def save(self, *args, **kwargs):
        if not self.employee_id:
            last_emp = User.objects.order_by("-id").first()
            if last_emp and last_emp.employee_id:
                last_id = int(last_emp.employee_id.replace("EMP", ""))
                new_id = last_id + 1
            else:
                new_id = 1
            self.employee_id = f"EMP{new_id:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee_id} - {self.username} ({self.role})"

