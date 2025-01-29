from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal
import json

from accounts.models import User
from tags.models import Tag

from .manager import JobManager

JOB_TYPE = (("1", "Full time"), ("2", "Part time"), ("3", "Internship"))
POSTING_TYPE = (("internal", "Internal Only"), ("external", "External Only"), ("both", "Both Internal and External"))

User = get_user_model()


class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    file_no = models.CharField("File Number", max_length=50, unique=True)
    id_no = models.CharField("ID Number", max_length=50, null=True, blank=True)
    pid_no = models.CharField("Personal ID Number", max_length=50, null=True, blank=True)
    tin_no = models.CharField("TIN Number", max_length=50, null=True, blank=True)
    name_of_employee = models.CharField("Employee Name", max_length=200)
    name_of_employee_in_amharic = models.CharField("Employee Name (Amharic)", max_length=200, null=True, blank=True)
    sex = models.CharField("Gender", max_length=1)
    date_of_birth = models.DateField("Date of Birth", null=True, blank=True)
    date_of_employment = models.DateField("Employment Date")
    job_category = models.CharField(max_length=100, null=True, blank=True)
    previous_position = models.CharField(max_length=100, null=True, blank=True)
    new_position = models.CharField("Current Position", max_length=100)
    old_jg = models.CharField("Old Job Grade", max_length=50, null=True, blank=True)
    new_jg = models.CharField("Current Job Grade", max_length=50, null=True, blank=True)
    working_unit = models.CharField("Department/Unit", max_length=100)
    district = models.CharField(max_length=100, null=True, blank=True)
    place_of_assignment = models.CharField(max_length=200, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    july_promoted_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    new_salary = models.DecimalField("Current Salary", max_digits=10, decimal_places=2, null=True, blank=True)
    old_salary_2022_23_inc = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    old_salary_2021_22_inc = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    old_salary_2020_2021 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    old_salary_2019_2020 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    old_salary_2018_2019 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    old_salary_2017_18 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    old_salary_2016_17 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    educational_level = models.CharField(max_length=100, null=True, blank=True)
    field_of_study = models.CharField(max_length=200, null=True, blank=True)
    university_college = models.CharField(max_length=200, null=True, blank=True)
    year_of_graduation = models.IntegerField(null=True, blank=True)
    cost_sharing_status = models.CharField(max_length=100, null=True, blank=True)
    processed_by = models.CharField(max_length=100, null=True, blank=True)
    branch_grading = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name_of_employee} ({self.file_no})"

    class Meta:
        verbose_name = "Employee Profile"
        verbose_name_plural = "Employee Profiles"
        ordering = ['file_no']


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class Job(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    description = models.TextField()
    location = models.CharField(max_length=150, blank=True, null=True)
    type = models.CharField(choices=JOB_TYPE, max_length=10, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    last_date = models.DateTimeField(blank=True, null=True)
    company_name = models.CharField(max_length=100, blank=True, null=True)
    company_description = models.CharField(max_length=300, blank=True, null=True)
    website = models.CharField(max_length=100, default="", blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    filled = models.BooleanField(default=False)
    salary = models.IntegerField(default=0, blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    vacancy = models.IntegerField(default=1, blank=True, null=True)
    posting_type = models.CharField(choices=POSTING_TYPE, max_length=10, default="external", blank=True)

    objects = JobManager()

    class Meta:
        ordering = ["id"]

    def get_absolute_url(self):
        return reverse("jobs:jobs-detail", args=[self.id])

    def __str__(self):
        return self.title


class Applicant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applicants")
    created_at = models.DateTimeField(default=timezone.now)
    comment = models.TextField(blank=True, null=True)
    status = models.SmallIntegerField(default=1)

    class Meta:
        ordering = ["id"]
        unique_together = ["user", "job"]

    def __str__(self):
        return self.user.get_full_name()

    @property
    def get_status(self):
        if self.status == 1:
            return "Pending"
        elif self.status == 2:
            return "Accepted"
        else:
            return "Rejected"


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    job = models.ForeignKey('Job', on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.job.title}"


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)


class ImportError(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    row_number = models.IntegerField()
    employee_name = models.CharField(max_length=255)
    file_no = models.CharField(max_length=100, blank=True, null=True)
    error_type = models.CharField(max_length=100)
    error_message = models.TextField()
    raw_values = models.JSONField(encoder=DecimalEncoder)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Import Error Log'
        verbose_name_plural = 'Import Error Logs'

    def __str__(self):
        return f"Error for {self.employee_name} at row {self.row_number}"

    @property
    def error_description(self):
        """Provides a human-readable description of the error"""
        if 'UNIQUE constraint' in self.error_message:
            if 'user_id' in self.error_message:
                return "A user account already exists for this employee. This usually happens when an employee record was previously imported."
            if 'file_no' in self.error_message:
                return "An employee with this file number already exists in the system."
            
        if 'NOT NULL constraint' in self.error_message:
            field = self.error_message.split('.')[-1].strip()
            return f"Required field '{field}' is missing or empty."
            
        if 'invalid literal for int()' in self.error_message:
            if 'year_of_graduation' in self.error_message:
                return "The graduation year is not in a valid format. It should be a four-digit year (e.g., 2020)."
            return "A numeric field contains invalid data that couldn't be converted to a number."
            
        if 'database is locked' in self.error_message:
            return "The database was temporarily locked. This is usually a temporary issue - please try importing this record again."
            
        if 'invalid date format' in self.error_message or 'time data' in self.error_message:
            return "A date field contains an invalid date format. Dates should be in YYYY-MM-DD format."
            
        if 'Decimal' in self.error_message and 'invalid' in self.error_message:
            return "A salary field contains invalid data. Salary should be a number without currency symbols."
            
        if 'Object of type Decimal is not JSON serializable' in self.error_message:
            return "A decimal number (like salary) couldn't be properly saved. This is a technical issue that has been automatically handled."
            
        return "An unexpected error occurred during import. Please check the raw data and error message for details."


class Audit(models.Model):
    ACTION_CHOICES = (
        ('INSERT', 'Insert'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
    )
    
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    table_name = models.CharField(max_length=50)  # The table being audited
    record_id = models.IntegerField()  # ID of the record being audited
    old_values = models.JSONField(null=True, blank=True)  # Previous values for updates/deletes
    new_values = models.JSONField(null=True, blank=True)  # New values for inserts/updates
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} on {self.table_name} #{self.record_id} at {self.timestamp}"
