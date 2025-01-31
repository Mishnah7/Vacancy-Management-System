from rest_framework.permissions import BasePermission
import logging

from jobsapp.models import Job

logger = logging.getLogger(__name__)


class IsEmployer(BasePermission):
    message = "Only employers can perform this action."

    def has_permission(self, request, view):
        is_employer = bool(request.user and request.user.role == "employer")
        logger.debug(f"IsEmployer check for user {request.user.id}: {is_employer}")
        return is_employer


class IsEmployee(BasePermission):
    message = "Only employees can perform this action."

    def has_permission(self, request, view):
        is_employee = bool(request.user and request.user.role == "employee")
        logger.debug(f"IsEmployee check for user {request.user.id}: {is_employee}")
        return is_employee


class IsJobCreator(BasePermission):
    message = "You can only modify jobs that you have created."

    def has_permission(self, request, view):
        # First check if user is authenticated
        is_authenticated = bool(request.user and request.user.is_authenticated)
        if not is_authenticated:
            logger.debug(f"IsJobCreator: User not authenticated")
            return False

        # For non-detail endpoints that create new jobs, allow authenticated users
        if request.method == 'POST':
            logger.debug(f"IsJobCreator: Allowing POST request for authenticated user {request.user.id}")
            return True

        # For list endpoint, filter queryset instead of blocking access
        if getattr(view, 'action', None) == 'list':
            logger.debug(f"IsJobCreator: Allowing LIST request for authenticated user {request.user.id}")
            return True

        # For other methods (PUT, PATCH, DELETE), check object permission
        # The object permission will be checked by has_object_permission
        logger.debug(f"IsJobCreator: Allowing request to proceed to object permission check for user {request.user.id}")
        return True

    def has_object_permission(self, request, view, obj):
        is_creator = obj.user == request.user
        logger.debug(f"IsJobCreator object check for user {request.user.id} on job {obj.id}: {is_creator}")
        return is_creator
