from rest_framework.permissions import BasePermission

from jobsapp.models import Job


class IsEmployer(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == "employer"


class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.role == "employee"


class IsJobCreator(BasePermission):
    def has_permission(self, request, view):
        # For non-detail endpoints, just check if user is authenticated
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # For detail endpoints (like delete), check if user owns the job
        return obj.user == request.user
