from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib import messages
from .models import User

class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'gender')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role', 'first_name', 'last_name', 'gender'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    actions = ['delete_selected_users']
    list_per_page = 30

    def delete_selected_users(self, request, queryset):
        if not request.user.is_superuser:
            messages.error(request, "Only superusers can delete users.")
            return

        # Don't allow deleting superusers
        if queryset.filter(is_superuser=True).exists():
            messages.error(request, "Superusers cannot be deleted.")
            return

        deleted_count = queryset.count()
        queryset.delete()
        messages.success(request, f'Successfully deleted {deleted_count} user(s).')
    delete_selected_users.short_description = "Delete selected users"

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not request.user.is_superuser:
            if 'delete_selected_users' in actions:
                del actions['delete_selected_users']
        return actions

    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete users
        if not request.user.is_superuser:
            return False
        # Don't allow deleting superusers
        if obj and obj.is_superuser:
            return False
        return True

admin.site.register(User, CustomUserAdmin)
