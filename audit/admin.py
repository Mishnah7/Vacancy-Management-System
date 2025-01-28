from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'content_type', 'object_id', 'ip_address')
    list_filter = ('action', 'timestamp', 'content_type', 'user')
    search_fields = ('user__email', 'ip_address', 'description')
    readonly_fields = ('timestamp', 'user', 'action', 'content_type', 'object_id', 'ip_address', 'changes', 'description')
    date_hierarchy = 'timestamp'
    list_per_page = 50
    
    def has_add_permission(self, request):
        return False
        
    def has_delete_permission(self, request, obj=None):
        return False
        
    def has_change_permission(self, request, obj=None):
        return False
