from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.core.exceptions import ValidationError


class JobManager(models.Manager):
    def filled(self, *args, **kwargs):
        return self.filter(filled=True, *args, **kwargs)

    def unfilled(self, *args, **kwargs):
        return self.filter(
            Q(filled=False) & 
            Q(last_date__gte=timezone.now()),
            *args, **kwargs
        )
    
    def for_user(self, user=None):
        """Get jobs visible to a specific user"""
        queryset = self.unfilled()
        
        if user and user.is_authenticated:
            try:
                from .models import EmployeeProfile
                employee = EmployeeProfile.objects.get(user=user)
                # Internal employees can see internal and both types
                return queryset.filter(posting_type__in=['internal', 'both'])
            except EmployeeProfile.DoesNotExist:
                # External users can see external and both types
                return queryset.filter(posting_type__in=['external', 'both'])
        
        # Unauthenticated users can only see external postings
        return queryset.filter(posting_type='external')
    
    def search(self, position=None, location=None):
        """Search jobs by position and/or location"""
        queryset = self.unfilled()
        
        if position:
            queryset = queryset.filter(title__icontains=position)
        if location:
            queryset = queryset.filter(location__icontains=location)
            
        return queryset.order_by("-created_at")

    def create_job(self, user, title, description, **kwargs):
        """
        Create a new job with validation
        
        Args:
            user: The user creating the job
            title: Job title
            description: Job description
            **kwargs: Additional job fields
            
        Returns:
            Job instance
            
        Raises:
            ValidationError: If validation fails
        """
        if not user or not title or not description:
            raise ValidationError("User, title and description are required")
            
        if len(title) < 5:
            raise ValidationError("Job title must be at least 5 characters long")
            
        if len(description) < 100:
            raise ValidationError("Job description must be at least 100 characters long")
            
        # Set default last_date if not provided
        if 'last_date' not in kwargs:
            kwargs['last_date'] = timezone.now() + timezone.timedelta(days=30)
            
        # Validate salary
        if 'salary' in kwargs and kwargs['salary'] is not None:
            if kwargs['salary'] < 0:
                raise ValidationError("Salary cannot be negative")
                
        # Validate vacancy
        if 'vacancy' in kwargs and kwargs['vacancy'] is not None:
            if kwargs['vacancy'] < 1:
                raise ValidationError("Number of vacancies must be at least 1")
                
        # Create the job
        job = self.model(
            user=user,
            title=title,
            description=description,
            **kwargs
        )
        job.full_clean()
        job.save()
        
        return job

    def active(self):
        """Get all active job postings (not filled and not expired)"""
        return self.filter(
            filled=False,
            last_date__gte=timezone.now()
        )

    def expired(self):
        """Get all expired job postings"""
        return self.filter(
            last_date__lt=timezone.now()
        )

    def filled(self):
        """Get all filled job postings"""
        return self.filter(filled=True)
