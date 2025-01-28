from datetime import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags

from jobsapp.models import Applicant, Job, JOB_TYPE, POSTING_TYPE


class CreateJobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            "title",
            "description",
            "location",
            "type",
            "category",
            "last_date",
            "company_name",
            "company_description",
            "website",
            "salary",
            "tags",
            "vacancy",
            "posting_type",
        ]
        labels = {
            "last_date": "Last Date",
            "company_name": "Company Name",
            "company_description": "Company Description",
            "tags": "Required Skills",
            "type": "Job Type",
            "posting_type": "Posting Type",
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter job title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter job description',
                'rows': 5
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter job location'
            }),
            'type': forms.Select(attrs={
                'class': 'form-control select2'
            }, choices=JOB_TYPE),
            'category': forms.Select(attrs={
                'class': 'form-control select2'
            }, choices=[
                ('web-design', 'Web Design'),
                ('graphic-design', 'Graphic Design'),
                ('web-development', 'Web Development'),
                ('human-resource', 'Human Resources'),
                ('support', 'Support'),
                ('android', 'Android Development')
            ]),
            'last_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company name'
            }),
            'company_description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company description',
                'rows': 3
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter company website (e.g., https://example.com)'
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter salary amount'
            }),
            'tags': forms.SelectMultiple(attrs={
                'class': 'form-control select2',
                'data-placeholder': 'Select required skills'
            }),
            'vacancy': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter number of vacancies',
                'min': 1
            }),
            'posting_type': forms.Select(attrs={
                'class': 'form-control select2'
            }, choices=POSTING_TYPE)
        }
        help_texts = {
            'title': 'Enter a clear and concise job title',
            'description': 'Provide a detailed description of the job responsibilities and requirements',
            'location': 'Specify the job location or "Remote" if applicable',
            'type': 'Select the type of employment',
            'category': 'Choose the job category that best fits this position',
            'last_date': 'Set the application deadline',
            'company_name': 'Enter your company name',
            'company_description': 'Provide a brief description of your company',
            'website': 'Enter your company website URL (optional)',
            'salary': 'Enter the salary amount (optional)',
            'tags': 'Select up to 6 required skills for this position',
            'vacancy': 'Enter the number of positions available',
            'posting_type': 'Choose who can view and apply for this position'
        }

    def is_valid(self):
        valid = super(CreateJobForm, self).is_valid()
        return valid

    def clean_last_date(self):
        date = self.cleaned_data.get("last_date")
        if not date:
            raise ValidationError("Last date is required")
        
        if date.date() < datetime.now().date():
            raise ValidationError("Last date cannot be before today")
        return date

    def clean_tags(self):
        tags = self.cleaned_data.get("tags", [])
        if len(tags) > 6:
            raise ValidationError("You can't add more than 6 skills")
        return tags

    def clean_website(self):
        website = self.cleaned_data.get("website", "")
        if website and not website.startswith("http://") and not website.startswith("https://"):
            website = "https://" + website
        return website

    def clean_title(self):
        title = self.cleaned_data.get("title")
        if len(title) < 5:
            raise ValidationError("Job title must be at least 5 characters long")
        return title

    def clean_description(self):
        description = self.cleaned_data.get("description")
        if not description:
            raise ValidationError("Job description is required")
            
        # Strip HTML tags for length validation
        plain_text = strip_tags(description)
        if len(plain_text.strip()) < 100:
            raise ValidationError("Job description must be at least 100 characters long to be meaningful")
        return description

    def clean_company_description(self):
        description = self.cleaned_data.get("company_description")
        if description:
            plain_text = strip_tags(description)
            if len(plain_text.strip()) < 10:  # Minimum length for company description
                raise ValidationError("Company description must be at least 10 characters long")
        return description

    def clean_salary(self):
        salary = self.cleaned_data.get("salary")
        if salary is not None and salary < 0:
            raise ValidationError("Salary cannot be negative")
        return salary

    def clean_vacancy(self):
        vacancy = self.cleaned_data.get("vacancy")
        if vacancy is not None and vacancy < 1:
            raise ValidationError("Number of vacancies must be at least 1")
        return vacancy

    def clean(self):
        cleaned_data = super().clean()
        
        # Validate posting type and company name relationship
        posting_type = cleaned_data.get('posting_type')
        company_name = cleaned_data.get('company_name')
        
        if posting_type in ['external', 'both'] and not company_name:
            self.add_error('company_name', 'Company name is required for external job postings')
            
        return cleaned_data

    def save(self, commit=True):
        job = super(CreateJobForm, self).save(commit=False)
        if commit:
            job.save()
            job.tags.clear()
            for tag in self.cleaned_data.get("tags", []):
                job.tags.add(tag)
        return job


class ApplyJobForm(forms.ModelForm):
    class Meta:
        model = Applicant
        fields = ("job",)


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.CharField(max_length=200)
    message = forms.CharField(widget=forms.Textarea)

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        email = cleaned_data.get('email')
        subject = cleaned_data.get('subject')
        message = cleaned_data.get('message')

        if not all([name, email, subject, message]):
            raise forms.ValidationError('All fields are required.')
        return cleaned_data
