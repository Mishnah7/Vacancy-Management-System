from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.contrib.auth import get_user_model
from django.db.models import Model
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

def serialize_datetime(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return obj

def serialize_value(value):
    """Serialize a single value, handling special cases"""
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    elif isinstance(value, Model):
        return str(value)
    elif isinstance(value, (list, tuple)):
        return [serialize_value(item) for item in value]
    return value

def serialize_model_dict(instance):
    """Convert model instance to dict with proper serialization of all fields"""
    data = model_to_dict(instance)
    return {k: serialize_value(v) for k, v in data.items()}

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
        old_values=old_values,
        new_values=new_values,
        ip_address=ip_address
    )

# Dictionary to store pre-save states
_pre_save_states = {}

def handle_pre_save(sender, instance, **kwargs):
    """Store the pre-save state of the instance"""
    if instance.id:  # If this is an update
        try:
            old_instance = sender.objects.get(id=instance.id)
            _pre_save_states[f"{sender.__name__}_{instance.id}"] = serialize_model_dict(old_instance)
        except sender.DoesNotExist:
            _pre_save_states[f"{sender.__name__}_{instance.id}"] = None

def handle_post_save(sender, instance, created, **kwargs):
    """Handle post-save audit logging"""
    if created:
        # Insert
        create_audit_log(
            instance=instance,
            action='INSERT',
            new_values=serialize_model_dict(instance)
        )
    else:
        # Update
        key = f"{sender.__name__}_{instance.id}"
        if key in _pre_save_states:
            create_audit_log(
                instance=instance,
                action='UPDATE',
                old_values=_pre_save_states[key],
                new_values=serialize_model_dict(instance)
            )
            del _pre_save_states[key]

def handle_post_delete(sender, instance, **kwargs):
    """Handle post-delete audit logging"""
    create_audit_log(
        instance=instance,
        action='DELETE',
        old_values=serialize_model_dict(instance)
    )

# Register signals for all relevant models
AUDITED_MODELS = [User, EmployeeProfile, Job, Applicant, Favorite]

for model in AUDITED_MODELS:
    pre_save.connect(handle_pre_save, sender=model)
    post_save.connect(handle_post_save, sender=model)
    post_delete.connect(handle_post_delete, sender=model) 