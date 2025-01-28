from django.contrib.auth.models import AbstractUser
from django.db import models

from accounts.managers import UserManager

GENDER_CHOICES = (("male", "Male"), ("female", "Female"))

ROLE_CHOICES = (
    ("admin", "Admin"),
    ("employer", "Employer"),
    ("employee", "Employee")
)

class User(AbstractUser):
    username = None
    role = models.CharField(max_length=12, choices=ROLE_CHOICES, error_messages={"required": "Role must be provided"})
    gender = models.CharField(max_length=10, blank=True, null=True, default="")
    email = models.EmailField(
        unique=True, blank=False, error_messages={"unique": "A user with that email already exists."}
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    objects = UserManager()

    def is_admin(self):
        return self.role == "admin"

    def is_employer(self):
        return self.role == "employer"

    def is_employee(self):
        return self.role == "employee"
