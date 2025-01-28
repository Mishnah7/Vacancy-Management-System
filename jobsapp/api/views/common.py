from django.http import JsonResponse
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
import logging

from ...models import Job
from ..serializers import JobSerializer
from ..permissions import IsEmployer, IsJobCreator

logger = logging.getLogger(__name__)


class JobViewSet(viewsets.ModelViewSet):
    serializer_class = JobSerializer
    queryset = serializer_class.Meta.model.objects.all()

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAuthenticated(), IsEmployer(), IsJobCreator()]
        return [AllowAny()]

    def get_queryset(self):
        if self.action == 'destroy':
            return self.queryset.filter(user=self.request.user)
        return self.queryset.filter(filled=False)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            
            # Check object permissions
            self.check_object_permissions(request, instance)
            
            # Log the deletion attempt
            logger.info(f"User {request.user.id} attempting to delete job {instance.id}")
            
            # Check if job has any applicants
            if instance.applicants.exists():
                logger.warning(f"Job {instance.id} has applicants but is being deleted")
            
            # Perform the deletion
            self.perform_destroy(instance)
            
            # Log successful deletion
            logger.info(f"Job {instance.id} successfully deleted by user {request.user.id}")
            
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            logger.error(f"Error deleting job: {str(e)}")
            return Response(
                {"error": "Failed to delete job posting. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SearchApiView(ListAPIView):
    serializer_class = JobSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        if "location" in self.request.GET and "position" in self.request.GET:
            return self.serializer_class.Meta.model.objects.unfilled(
                location__contains=self.request.GET["location"], title__contains=self.request.GET["position"]
            )
        else:
            return self.serializer_class.Meta.model.objects.unfilled()


@api_view(["GET"])
@permission_classes([AllowAny])
def categories_list_api_view(request):
    categories = [
        {"name": "Web design", "slug": "web-design", "icon": "lni-brush"},
        {"name": "Graphic design", "slug": "graphic-design", "icon": "lni-heart"},
        {"name": "Web development", "slug": "web-development", "icon": "lni-funnel"},
        {"name": "Human Resource", "slug": "human-resource", "icon": "lni-cup"},
        {"name": "Support", "slug": "support", "icon": "lni-home"},
        {"name": "Android Development", "slug": "android", "icon": "lni-world"},
    ]

    for category in categories:
        total_jobs = Job.objects.filter(category=category.get("slug")).count()
        category["total_jobs"] = total_jobs

    return JsonResponse(categories, safe=False)
