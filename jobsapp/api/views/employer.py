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
        logger.info("="*50)
        logger.info("JOB DELETION ATTEMPT")
        logger.info("="*50)
        
        try:
            # Get the job
            try:
                job = Job.objects.select_related('user').get(id=job_id)
                logger.info(f"Job found - ID: {job_id}")
            except Job.DoesNotExist:
                logger.warning(f"Job {job_id} not found")
                return JsonResponse(
                    {"error": "Job not found"},
                    status=404
                )
            
            # Check object permissions
            if not request.user.is_employer():
                logger.warning("Permission denied - User is not an employer")
                return JsonResponse(
                    {"error": "Only employers can delete jobs"},
                    status=403
                )
                
            if job.user_id != request.user.id:
                logger.warning("Permission denied - Job owner mismatch")
                return JsonResponse(
                    {"error": "You can only delete your own jobs"},
                    status=403
                )
            
            # Delete the job
            logger.info("Permission checks passed, proceeding with deletion")
            job.delete()
            logger.info(f"Job {job_id} deleted successfully")
            logger.info("="*50)
            
            return JsonResponse(
                {"message": "Job deleted successfully"},
                status=200
            )
            
        except Exception as e:
            logger.error("="*50)
            logger.error("Unexpected error during job deletion")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error("="*50)
            return JsonResponse(
                {"error": "Failed to delete job. Please try again."},
                status=500
            )
