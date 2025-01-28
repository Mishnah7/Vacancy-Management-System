from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings

User = get_user_model()

class AuditLog(models.Model):
    ACTION_CHOICES = (
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('PASSWORD_RESET', 'Password Reset'),
        ('PASSWORD_CHANGE', 'Password Change'),
        ('AUTH_FAIL', 'Authentication Failure'),
        ('ROLE_CHANGE', 'Role Change')
    )

    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    action = models.CharField(max_length=64, null=True, blank=True)
    object_type = models.CharField(max_length=255, null=True, blank=True)
    object_id = models.CharField(max_length=255, null=True, blank=True)
    object_repr = models.CharField(max_length=255, null=True, blank=True)
    changes = models.JSONField(null=True)
    ip_address = models.GenericIPAddressField(null=True)
    user_agent = models.TextField(
        verbose_name='User Agent',
        help_text='Client browser and OS information'
    )
    device_hash = models.CharField(
        max_length=64,
        blank=True,
        verbose_name='Device Fingerprint'
    )
    country_code = models.CharField(
        max_length=3,
        blank=True,
        verbose_name='Geolocation Code'
    )
    
    # For tracking the specific object that was modified
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Additional context
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'
        
    def __str__(self):
        return f"{self.timestamp} - {self.user} - {self.action} - {self.object_type}"
