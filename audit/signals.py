from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from .models import AuditLog

User = get_user_model()

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@receiver(post_save)
def log_save(sender, instance, created, **kwargs):
    # Skip logging AuditLog changes to avoid recursion
    if sender == AuditLog:
        return
        
    try:
        user = None
        if hasattr(instance, 'request'):
            user = instance.request.user if instance.request.user.is_authenticated else None
            
        content_type = ContentType.objects.get_for_model(sender)
        
        # Determine what fields changed
        if not created and hasattr(instance, '_loaded_values'):
            changes = {}
            for field, value in instance._loaded_values.items():
                if getattr(instance, field) != value:
                    changes[field] = {
                        'old': value,
                        'new': getattr(instance, field)
                    }
        else:
            changes = None
            
        AuditLog.objects.create(
            user=user,
            action='CREATE' if created else 'UPDATE',
            content_type=content_type,
            object_id=instance.pk,
            changes=changes,
            description=f"{'Created' if created else 'Updated'} {sender.__name__} with id {instance.pk}"
        )
    except Exception as e:
        print(f"Error logging change: {e}")

@receiver(post_delete)
def log_delete(sender, instance, **kwargs):
    if sender == AuditLog:
        return
        
    try:
        user = None
        if hasattr(instance, 'request'):
            user = instance.request.user if instance.request.user.is_authenticated else None
            
        content_type = ContentType.objects.get_for_model(sender)
        
        AuditLog.objects.create(
            user=user,
            action='DELETE',
            content_type=content_type,
            object_id=instance.pk,
            description=f"Deleted {sender.__name__} with id {instance.pk}"
        )
    except Exception as e:
        print(f"Error logging deletion: {e}")

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    AuditLog.objects.create(
        user=user,
        action='LOGIN',
        ip_address=get_client_ip(request),
        description=f"User {user.email} logged in"
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    AuditLog.objects.create(
        user=user,
        action='LOGOUT',
        ip_address=get_client_ip(request),
        description=f"User {user.email} logged out"
    ) 