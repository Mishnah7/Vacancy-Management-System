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


class JobDeleteAPIView(DestroyAPIView):
    queryset = Job.objects.all()
    permission_classes = [IsAuthenticated, IsEmployer, IsJobCreator]
    authentication_classes = [SessionAuthentication]
    lookup_field = 'id'
    lookup_url_kwarg = 'job_id'

    def get_queryset(self):
        return self.queryset.filter(user_id=self.request.user.id)

    def get_object(self):
        """
        Override get_object to match the URL parameter with lookup field
        """
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        job_id = self.kwargs[lookup_url_kwarg]
        logger.info(f"Looking up job with ID: {job_id}")
        logger.info(f"Current user: {self.request.user.id}, role: {self.request.user.role}")
        
        try:
            obj = self.get_queryset().get(id=job_id)
            logger.info(f"Found job: {obj.id}, owned by user: {obj.user_id}")
            
            # Manual permission check
            if obj.user_id != self.request.user.id:
                logger.warning(f"Permission denied: Job {obj.id} belongs to user {obj.user_id}, not {self.request.user.id}")
                raise PermissionDenied("You do not have permission to delete this job")
                
            return obj
        except Job.DoesNotExist:
            logger.warning(f"Job {job_id} not found")
            raise Http404("Job not found")
        except Exception as e:
            logger.error(f"Error getting job {job_id}: {str(e)}")
            raise

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            logger.info(f"Deleting job {instance.id} by user {request.user.id}")
            self.perform_destroy(instance)
            return Response(
                {"message": "Job deleted successfully"},
                status=status.HTTP_200_OK
            )
        except Http404:
            return Response(
                {"error": "Job not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except PermissionDenied as e:
            logger.warning(f"Permission denied for user {request.user.id}: {str(e)}")
            return Response(
                {"error": "You do not have permission to delete this job"},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            logger.error(f"Error deleting job: {str(e)}")
            return Response(
                {"error": "Failed to delete job", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
