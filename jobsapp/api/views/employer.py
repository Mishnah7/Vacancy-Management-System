from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, ListAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404
import logging
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.contrib.auth import get_user_model
import traceback

from jobsapp.api.permissions import IsEmployer, IsJobCreator
from jobsapp.api.serializers import ApplicantSerializer, DashboardJobSerializer, NewJobSerializer
from jobsapp.models import Applicant, Job

logger = logging.getLogger(__name__)


class DashboardAPIView(ListAPIView):
    serializer_class = DashboardJobSerializer
    permission_classes = [IsAuthenticated, IsEmployer]

    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.filter(user_id=self.request.user.id)


class JobCreateAPIView(CreateAPIView):
    serializer_class = NewJobSerializer
    permission_classes = [IsAuthenticated, IsEmployer]


class ApplicantsListAPIView(ListAPIView):
    serializer_class = ApplicantSerializer
    permission_classes = [IsAuthenticated, IsEmployer]

    def get_queryset(self):
        user = self.request.user
        return Applicant.objects.filter(job__user_id=user.id)


class ApplicantsPerJobListAPIView(ListAPIView):
    serializer_class = ApplicantSerializer
    permission_classes = [IsAuthenticated, IsEmployer, IsJobCreator]

    def get_queryset(self):
        return Applicant.objects.filter(job_id=self.kwargs["job_id"]).order_by("id")


class UpdateApplicantStatusAPIView(APIView):
    permission_classes = [IsAuthenticated, IsEmployer]

    def post(self, request, *args, **kwargs):
        applicant_id = kwargs.get("applicant_id")
        status_code = kwargs.get("status_code")
        try:
            applicant = Applicant.objects.select_related("job__user").get(id=applicant_id)
        except Applicant.DoesNotExist:
            data = {"message": "Applicant not found"}
            return JsonResponse(data, status=404)

        if applicant.job.user != request.user:
            data = {"errors": "You are not authorized"}
            return JsonResponse(data, status=403)
        if status_code not in [1, 2]:
            status_code = 3

        applicant.status = status_code
        applicant.comment = request.data.get("comment", "")
        applicant.save()
        data = {"message": "Applicant status updated"}
        return JsonResponse(data, status=200)


class JobDeleteAPIView(APIView):
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated, IsEmployer, IsJobCreator]
    
    def delete(self, request, job_id):
        """Delete a job posting with proper error handling and logging."""
        logger.info("="*50)
        logger.info(f"Job deletion initiated for job_id: {job_id} by user: {request.user.id}")
        
        try:
            # Attempt to fetch the job with select_related to minimize db queries
            job = Job.objects.select_related('user').get(id=job_id)
            
            # Log permission check
            logger.info(f"Found job {job_id} owned by user {job.user.id}")
            
            # Check if user has permission (this is also handled by IsJobCreator, but we log it)
            if job.user.id != request.user.id:
                logger.warning(f"Permission denied: User {request.user.id} attempted to delete job {job_id} owned by user {job.user.id}")
                return JsonResponse(
                    {"error": "You don't have permission to delete this job"}, 
                    status=403
                )
            
            # Store job owner's ID for cache clearing
            job_owner_id = job.user.id
            
            # Perform the deletion
            job.delete()
            
            # Clear relevant caches
            cache.delete(f'trending_jobs_{job_owner_id}')
            cache.delete('trending_jobs_anon')
            
            logger.info(f"Successfully deleted job {job_id} and cleared associated caches")
            logger.info("="*50)
            
            return JsonResponse({"message": "Job deleted successfully"}, status=200)
            
        except Job.DoesNotExist:
            logger.warning(f"Job deletion failed: Job {job_id} not found")
            logger.info("="*50)
            return JsonResponse(
                {"error": "Job not found"}, 
                status=404
            )
            
        except PermissionDenied as e:
            logger.warning(f"Permission denied: {str(e)}")
            logger.info("="*50)
            return JsonResponse(
                {"error": "You don't have permission to perform this action"}, 
                status=403
            )
            
        except Exception as e:
            logger.error("="*50)
            logger.error(f"Unexpected error during job deletion: {type(e).__name__}")
            logger.error(f"Error details: {str(e)}")
            logger.error(traceback.format_exc())
            logger.error("="*50)
            return JsonResponse(
                {"error": "An unexpected error occurred while deleting the job"}, 
                status=500
            )
