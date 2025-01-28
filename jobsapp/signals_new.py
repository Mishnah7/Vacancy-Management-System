from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.contrib.auth import get_user_model
from .models import Audit, EmployeeProfile, Job, Applicant, Favorite
from .middleware import RequestMiddleware
from datetime import datetime, date

User = get_user_model()

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def serialize_value(val):
    if isinstance(val, (datetime, date)):
        return val.isoformat()
    return val

def serialize_dict(d):
    return {k: serialize_value(v) for k, v in d.items()}

def create_audit_log(instance, action, old_values=None, new_values=None):
    request = RequestMiddleware.get_request()
    
    # Get the current user from the request
    user = request.user if request and hasattr(request, 'user') else None
    
    # Get client IP if request is available
    ip_address = get_client_ip(request) if request else None
    
    # Create audit log with serialized values
    Audit.objects.create(
        user=user if user and user.is_authenticated else None,
        action=action,
        table_name=instance._meta.model_name,
        record_id=instance.id,
        old_values=serialize_dict(old_values) if old_values else None,
        new_values=serialize_dict(new_values) if new_values else None,
        ip_address=ip_address
    )

# Dictionary to store pre-save states
_pre_save_states = {}

def handle_pre_save(sender, instance, **kwargs):
    """Store the pre-save state of the instance"""
    if instance.id:  # If this is an update
        try:
            old_instance = sender.objects.get(id=instance.id)
            _pre_save_states[f"{sender.__name__}_{instance.id}"] = model_to_dict(old_instance)
        except sender.DoesNotExist:
            _pre_save_states[f"{sender.__name__}_{instance.id}"] = None

def handle_post_save(sender, instance, created, **kwargs):
    """Handle post-save audit logging"""
    if created:
        # Insert
        create_audit_log(
            instance=instance,
            action='INSERT',
            new_values=model_to_dict(instance)
        )
    else:
        # Update
        key = f"{sender.__name__}_{instance.id}"
        if key in _pre_save_states:
            create_audit_log(
                instance=instance,
                action='UPDATE',
                old_values=_pre_save_states[key],
                new_values=model_to_dict(instance)
            )
            del _pre_save_states[key]

def handle_post_delete(sender, instance, **kwargs):
    """Handle post-delete audit logging"""
    create_audit_log(
        instance=instance,
        action='DELETE',
        old_values=model_to_dict(instance)
    )

# Register signals for all relevant models
AUDITED_MODELS = [User, EmployeeProfile, Job, Applicant, Favorite]

for model in AUDITED_MODELS:
    pre_save.connect(handle_pre_save, sender=model)
    post_save.connect(handle_post_save, sender=model)
    post_delete.connect(handle_post_delete, sender=model) 