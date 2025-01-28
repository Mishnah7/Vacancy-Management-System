from django.contrib import admin
from django.contrib.flatpages.admin import FlatPageAdmin
from django.contrib.flatpages.models import FlatPage
from .models import Job, Applicant, Favorite, EmployeeProfile, ImportError, Audit
from django.utils.html import format_html, format_html_join
from django.db.models import Q
from django import forms
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import path
from django.core.management import call_command
from django.template.response import TemplateResponse

# Register your models here.

class TempIDFilter(admin.SimpleListFilter):
    title = 'Temporary ID Status'
    parameter_name = 'temp_id'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'Has Temporary ID'),
            ('no', 'Has Regular ID'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(file_no__startswith='TEMP-')
        if self.value() == 'no':
            return queryset.exclude(file_no__startswith='TEMP-')

class ImportEmployeesForm(forms.Form):
    sql_file = forms.FileField(
        label='SQL File',
        help_text='Select the SQL file containing employee data'
    )
    create_users = forms.BooleanField(
        required=False,
        initial=True,
        label='Create User Accounts',
        help_text='Create user accounts for imported employees'
    )
    clear_existing = forms.BooleanField(
        required=False,
        initial=False,
        label='Clear Existing Data',
        help_text='WARNING: This will delete all existing employee records before import'
    )

@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = (
        'file_no',
        'name_of_employee',
        'name_of_employee_in_amharic',
        'sex',
        'id_no',
        'pid_no',
        'tin_no',
        'date_of_birth',
        'date_of_employment',
        'job_category',
        'previous_position',
        'new_position',
        'old_jg',
        'new_jg',
        'working_unit',
        'district',
        'place_of_assignment',
        'region',
        'july_promoted_salary',
        'new_salary',
        'old_salary_2022_23_inc',
        'old_salary_2021_22_inc',
        'old_salary_2020_2021',
        'old_salary_2019_2020',
        'old_salary_2018_2019',
        'old_salary_2017_18',
        'old_salary_2016_17',
        'educational_level',
        'field_of_study',
        'university_college',
        'year_of_graduation',
        'cost_sharing_status',
        'processed_by',
        'branch_grading',
        'is_active',
        'user'
    )
    list_filter = (
        TempIDFilter,
        'is_active', 'working_unit', 'job_category', 'educational_level',
        'region', 'date_of_employment', 'sex'
    )
    search_fields = (
        'file_no', 'name_of_employee', 'name_of_employee_in_amharic',
        'id_no', 'pid_no', 'tin_no', 'new_position', 'working_unit'
    )
    ordering = ('file_no', 'name_of_employee')
    date_hierarchy = 'date_of_employment'
    list_per_page = 50
    
    def get_list_display(self, request):
        """Add custom styling for auto-generated file numbers"""
        def colored_file_no(obj):
            if obj.file_no.startswith('TEMP-'):
                return format_html(
                    '<span style="background-color: #2b5797; color: white; padding: 3px 8px; border-radius: 4px; font-weight: 500;" title="Auto-generated file number">{}</span>',
                    obj.file_no
                )
            return obj.file_no
        colored_file_no.short_description = 'File No'
        
        # Replace file_no with colored version
        display = list(super().get_list_display(request))
        file_no_index = display.index('file_no')
        display[file_no_index] = colored_file_no
        return display
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                ('file_no', 'is_active'),
                ('name_of_employee', 'name_of_employee_in_amharic'),
                ('sex', 'date_of_birth'),
                'user'
            ),
            'classes': ('wide',)
        }),
        ('Identification', {
            'fields': ('id_no', 'pid_no', 'tin_no'),
            'classes': ('wide',)
        }),
        ('Employment Details', {
            'fields': (
                'date_of_employment',
                ('job_category', 'new_position', 'previous_position'),
                ('old_jg', 'new_jg'),
                ('working_unit', 'district'),
                ('place_of_assignment', 'region')
            ),
            'classes': ('wide',)
        }),
        ('Salary History', {
            'fields': (
                ('new_salary', 'july_promoted_salary'),
                ('old_salary_2022_23_inc', 'old_salary_2021_22_inc'),
                ('old_salary_2020_2021', 'old_salary_2019_2020'),
                ('old_salary_2018_2019', 'old_salary_2017_18'),
                'old_salary_2016_17'
            ),
            'classes': ('wide',)
        }),
        ('Education', {
            'fields': (
                'educational_level',
                'field_of_study',
                'university_college',
                'year_of_graduation',
                'cost_sharing_status'
            ),
            'classes': ('wide',)
        }),
        ('Administrative', {
            'fields': (
                'processed_by',
                'branch_grading'
            ),
            'classes': ('wide',)
        })
    )
    
    readonly_fields = ('user',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-employees/', self.admin_site.admin_view(self.import_employees_view), name='import-employees'),
        ]
        return custom_urls + urls

    def import_employees_view(self, request):
        if request.method == 'POST':
            form = ImportEmployeesForm(request.POST, request.FILES)
            if form.is_valid():
                sql_file = request.FILES['sql_file']
                create_users = form.cleaned_data['create_users']
                clear_existing = form.cleaned_data['clear_existing']

                # Save the uploaded file temporarily
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.sql') as temp_file:
                    for chunk in sql_file.chunks():
                        temp_file.write(chunk)
                    temp_file_path = temp_file.name

                try:
                    # Clear existing data if requested
                    if clear_existing:
                        EmployeeProfile.objects.all().delete()
                        messages.info(request, "Cleared existing employee data")

                    # Run the import command
                    call_command(
                        'import_employees',
                        temp_file_path,
                        create_users=create_users
                    )

                    # Count results
                    total_employees = EmployeeProfile.objects.count()
                    temp_ids = EmployeeProfile.objects.filter(file_no__startswith='TEMP-').count()
                    recent_errors = ImportError.objects.order_by('-timestamp')[:5]

                    context = {
                        'title': 'Import Results',
                        'total_employees': total_employees,
                        'temp_ids': temp_ids,
                        'recent_errors': recent_errors,
                        'opts': self.model._meta,
                    }
                    
                    messages.success(request, f"Successfully imported {total_employees} employees ({temp_ids} with temporary IDs)")
                    if recent_errors.exists():
                        messages.warning(request, f"There were {recent_errors.count()} errors during import. Check the Import Error Log for details.")
                    
                    return TemplateResponse(
                        request,
                        'admin/jobsapp/employeeprofile/import_results.html',
                        context
                    )

                except Exception as e:
                    messages.error(request, f"Import failed: {str(e)}")
                finally:
                    # Clean up the temporary file
                    os.unlink(temp_file_path)

                return HttpResponseRedirect('../')
        else:
            form = ImportEmployeesForm()

        context = {
            'title': 'Import Employees',
            'form': form,
            'opts': self.model._meta,
            'has_file_field': True  # Required for proper form enctype
        }
        return TemplateResponse(
            request,
            'admin/jobsapp/employeeprofile/import_form.html',
            context
        )

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_import_button'] = True
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company_name', 'type', 'category', 'posting_type', 'last_date', 'filled')
    list_filter = ('type', 'category', 'posting_type', 'filled', 'created_at')
    search_fields = ('title', 'company_name', 'category', 'description')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description'),
            'description': 'These fields are required.'
        }),
        ('Job Details', {
            'fields': ('type', 'category', 'location', 'salary', 'vacancy'),
            'description': 'Optional details about the position.',
            'classes': ('collapse',)
        }),
        ('Company Information', {
            'fields': ('company_name', 'company_description', 'website'),
            'description': 'Optional information about the company.',
            'classes': ('collapse',)
        }),
        ('Skills & Requirements', {
            'fields': ('tags',),
            'description': 'Optional: Select or add required skills for this position. You can select multiple skills.',
            'classes': ('collapse',)
        }),
        ('Posting Settings', {
            'fields': ('posting_type', 'last_date', 'filled'),
            'description': 'Control who can see this job and when it expires.',
            'classes': ('collapse',)
        }),
        ('System Fields', {
            'fields': ('user', 'created_at'),
            'classes': ('collapse',),
            'description': 'Automatically managed fields.'
        })
    )
    
    readonly_fields = ('created_at',)
    filter_horizontal = ('tags',)
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only set the user during creation
            obj.user = request.user
        super().save_model(request, obj, form, change)

@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'created_at', 'status')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'job__title')
    date_hierarchy = 'created_at'

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'job__title')
    date_hierarchy = 'created_at'

@admin.register(ImportError)
class ImportErrorAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'employee_name', 'file_no', 'error_type', 'get_error_description')
    list_filter = ('timestamp', 'error_type')
    search_fields = ('employee_name', 'file_no', 'error_message')
    readonly_fields = ('timestamp', 'row_number', 'employee_name', 'file_no', 'error_type', 'error_message', 'error_description', 'raw_values_display')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def get_error_description(self, obj):
        return obj.error_description
    get_error_description.short_description = 'Error Description'

    def raw_values_display(self, obj):
        # Format raw values as an HTML table
        if not obj.raw_values:
            return "No raw values available"
            
        rows = []
        for idx, value in enumerate(obj.raw_values):
            formatted_value = value if value is not None else '<em>Empty</em>'
            rows.append(f'<tr><td style="padding-right: 10px;"><strong>Column {idx}</strong></td><td>{formatted_value}</td></tr>')
            
        return format_html(
            '<table style="border-collapse: collapse;">{}</table>',
            format_html_join('\n', '{}', ((row,) for row in rows))
        )
    raw_values_display.short_description = 'Raw Values'

    fieldsets = (
        ('Error Details', {
            'fields': ('timestamp', 'row_number', 'employee_name', 'file_no')
        }),
        ('Error Information', {
            'fields': ('error_type', 'error_message', 'error_description')
        }),
        ('Raw Data', {
            'fields': ('raw_values_display',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Audit)
class AuditAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'get_user', 'action', 'table_name', 'record_id', 'get_ip_address', 'get_change_description')
    list_filter = (
        'action',
        'table_name',
        ('timestamp', admin.DateFieldListFilter),
    )
    search_fields = (
        'user__username',
        'user__email',
        'table_name',
        'ip_address',
        'record_id',
    )
    readonly_fields = (
        'user',
        'action',
        'table_name',
        'record_id',
        'old_values_display',
        'new_values_display',
        'ip_address',
        'timestamp',
        'get_change_description',
    )
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    list_per_page = 50

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_user(self, obj):
        if obj.user:
            return f"{obj.user.username} ({obj.user.email})"
        return "System"
    get_user.short_description = 'User'
    get_user.admin_order_field = 'user__username'

    def get_ip_address(self, obj):
        return obj.ip_address or "N/A"
    get_ip_address.short_description = 'IP Address'
    get_ip_address.admin_order_field = 'ip_address'

    def get_change_description(self, obj):
        def get_record_identifier(values_dict):
            """Helper to get a human-readable record identifier"""
            identifiers = []
            priority_fields = ['name', 'title', 'username', 'email', 'file_no', 'id_no', 'name_of_employee']
            
            # First try priority fields
            for field in priority_fields:
                if values_dict and field in values_dict and values_dict[field]:
                    identifiers.append(f"{field}: {values_dict[field]}")
            
            # If no priority fields found, add other non-null values
            if not identifiers and values_dict:
                for key, value in values_dict.items():
                    if value and key not in ['created_at', 'updated_at', 'timestamp']:
                        identifiers.append(f"{key}: {value}")
                        if len(identifiers) >= 3:  # Limit to 3 identifiers
                            break
            
            return ", ".join(identifiers)

        if obj.action == 'DELETE':
            identifier = get_record_identifier(obj.old_values)
            return format_html(
                '<span style="color: #dc3545; font-weight: 500;">Deleted {} record #{} ({})</span>',
                obj.table_name, obj.record_id, identifier
            )
        elif obj.action == 'INSERT':
            identifier = get_record_identifier(obj.new_values)
            changes = []
            if obj.new_values:
                for key, value in obj.new_values.items():
                    if value is not None and key not in ['created_at', 'updated_at', 'timestamp']:
                        changes.append(f"{key}: {value}")
            changes_str = ", ".join(changes[:3])
            if len(changes) > 3:
                changes_str += "..."
            return format_html(
                '<span style="color: #28a745; font-weight: 500;">Created new {} record: {} with {}</span>',
                obj.table_name, identifier, changes_str
            )
        elif obj.action == 'UPDATE':
            identifier = get_record_identifier(obj.new_values)
            changes = []
            if obj.old_values and obj.new_values:
                for key in obj.new_values.keys():
                    if key in obj.old_values:
                        if obj.old_values[key] != obj.new_values[key]:
                            old_val = obj.old_values[key] or 'None'
                            new_val = obj.new_values[key] or 'None'
                            changes.append(f"{key}: {old_val} → {new_val}")
            changes_str = ", ".join(changes[:3])
            if len(changes) > 3:
                changes_str += "..."
            return format_html(
                '<span style="color: #ffc107; font-weight: 500;">Updated {} record: {} - Changes: {}</span>',
                obj.table_name, identifier, changes_str
            )
        return obj.action
    get_change_description.short_description = 'Change Description'

    def old_values_display(self, obj):
        if not obj.old_values:
            return "No previous values"
        rows = []
        for key, value in obj.old_values.items():
            new_value = obj.new_values.get(key) if obj.new_values else None
            if obj.action == 'UPDATE' and new_value != value:
                # Highlight changed values
                rows.append(
                    (
                        key,
                        format_html(
                            '<span style="color: #dc3545; text-decoration: line-through;">{}</span>',
                            value if value is not None else 'None'
                        )
                    )
                )
            else:
                rows.append((key, value if value is not None else 'None'))
        
        return format_html(
            '<table class="audit-values">{}</table>',
            format_html_join('\n', '<tr><th>{}</th><td>{}</td></tr>', rows)
        )
    old_values_display.short_description = 'Previous Values'

    def new_values_display(self, obj):
        if not obj.new_values:
            return "No new values"
        rows = []
        for key, value in obj.new_values.items():
            old_value = obj.old_values.get(key) if obj.old_values else None
            if obj.action == 'UPDATE' and old_value != value:
                # Highlight changed values
                rows.append(
                    (
                        key,
                        format_html(
                            '<span style="color: #28a745; font-weight: 500;">{}</span>',
                            value if value is not None else 'None'
                        )
                    )
                )
            else:
                rows.append((key, value if value is not None else 'None'))
        
        return format_html(
            '<table class="audit-values">{}</table>',
            format_html_join('\n', '<tr><th>{}</th><td>{}</td></tr>', rows)
        )
    new_values_display.short_description = 'New Values'

    fieldsets = (
        ('Audit Information', {
            'fields': (
                'timestamp',
                'user',
                'ip_address',
                'action',
                'table_name',
                'record_id',
                'get_change_description',
            )
        }),
        ('Changes', {
            'fields': (
                'old_values_display',
                'new_values_display',
            ),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    class Media:
        css = {
            'all': ('css/audit_admin.css',)
        }
