from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _


class Role(models.Model):
    ADMIN = 'admin'
    MANAGER = 'manager'
    EMPLOYEE = 'employee'

    ROLE_CHOICES = [
        (ADMIN, 'Admin'),
        (MANAGER, 'Manager'),
        (EMPLOYEE, 'Employee'),
    ]

    name = models.CharField(max_length=20, choices=ROLE_CHOICES, unique=True)

    def __str__(self) -> str:
        return self.get_name_display()


class User(AbstractUser):
    username_validator = UnicodeUsernameValidator()

    # Make username non-unique
    username = models.CharField(
        _("username"),
        max_length=150,
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
        validators=[username_validator],
        unique=False,
    )

    # Make email the unique identifier
    email = models.EmailField(_("email address"), unique=True, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

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
