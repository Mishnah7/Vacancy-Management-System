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
        is_authenticated = bool(request.user and request.user.is_authenticated)
        logger.debug(f"IsJobCreator authentication check for user {request.user.id}: {is_authenticated}")
        return is_authenticated

    def has_object_permission(self, request, view, obj):
        is_creator = obj.user == request.user
        logger.debug(f"IsJobCreator object check for user {request.user.id} on job {obj.id}: {is_creator}")
        return is_creator
