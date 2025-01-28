# Generated by Django 5.1.2 on 2025-01-27 05:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobsapp', '0014_job_posting_type_internalemployee'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='EmployeeProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_no', models.CharField(max_length=50, unique=True, verbose_name='File Number')),
                ('id_no', models.CharField(blank=True, max_length=50, null=True, verbose_name='ID Number')),
                ('pid_no', models.CharField(blank=True, max_length=50, null=True, verbose_name='Personal ID Number')),
                ('tin_no', models.CharField(blank=True, max_length=50, null=True, verbose_name='TIN Number')),
                ('name_of_employee', models.CharField(max_length=200, verbose_name='Employee Name')),
                ('name_of_employee_in_amharic', models.CharField(blank=True, max_length=200, null=True, verbose_name='Employee Name (Amharic)')),
                ('sex', models.CharField(max_length=1, verbose_name='Gender')),
                ('date_of_birth', models.DateField(blank=True, null=True, verbose_name='Date of Birth')),
                ('date_of_employment', models.DateField(verbose_name='Employment Date')),
                ('job_category', models.CharField(blank=True, max_length=100, null=True)),
                ('previous_position', models.CharField(blank=True, max_length=100, null=True)),
                ('new_position', models.CharField(max_length=100, verbose_name='Current Position')),
                ('old_jg', models.CharField(blank=True, max_length=50, null=True, verbose_name='Old Job Grade')),
                ('new_jg', models.CharField(blank=True, max_length=50, null=True, verbose_name='Current Job Grade')),
                ('working_unit', models.CharField(max_length=100, verbose_name='Department/Unit')),
                ('district', models.CharField(blank=True, max_length=100, null=True)),
                ('place_of_assignment', models.CharField(blank=True, max_length=200, null=True)),
                ('region', models.CharField(blank=True, max_length=100, null=True)),
                ('july_promoted_salary', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('new_salary', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Current Salary')),
                ('old_salary_2022_23_inc', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('old_salary_2021_22_inc', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('old_salary_2020_2021', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('old_salary_2019_2020', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('old_salary_2018_2019', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('old_salary_2017_18', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('old_salary_2016_17', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('educational_level', models.CharField(blank=True, max_length=100, null=True)),
                ('field_of_study', models.CharField(blank=True, max_length=200, null=True)),
                ('university_college', models.CharField(blank=True, max_length=200, null=True)),
                ('year_of_graduation', models.IntegerField(blank=True, null=True)),
                ('cost_sharing_status', models.CharField(blank=True, max_length=100, null=True)),
                ('processed_by', models.CharField(blank=True, max_length=100, null=True)),
                ('branch_grading', models.CharField(blank=True, max_length=100, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Employee Profile',
                'verbose_name_plural': 'Employee Profiles',
                'ordering': ['file_no'],
            },
        ),
        migrations.DeleteModel(
            name='InternalEmployee',
        ),
    ]
