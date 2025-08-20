from django.db import models
from django.contrib.auth.models import AbstractUser


class Role(models.Model):
    ADMIN = 'ADMIN'
    MANAGER = 'MANAGER'
    EMPLOYEE = 'EMPLOYEE'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (MANAGER, 'Manager'),
        (EMPLOYEE, 'Employee'),
    ]

    name = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)

    def __str__(self) -> str:
        return self.get_name_display()


class User(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name='users', null=True, blank=True)

    @property
    def is_admin(self) -> bool:
        return bool(self.role and self.role.name == Role.ADMIN)

    @property
    def is_manager(self) -> bool:
        return bool(self.role and self.role.name == Role.MANAGER)

    @property
    def is_employee(self) -> bool:
        return bool(self.role and self.role.name == Role.EMPLOYEE)

# Create your models here.
