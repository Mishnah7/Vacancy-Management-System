import json
import logging
from django.contrib.auth.decorators import login_required
from django.templatetags.static import static
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from django.views.decorators.clickjacking import xframe_options_deny
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.db import transaction
from django_ratelimit.decorators import ratelimit

from jobsapp.decorators import user_is_employee

# Create your views here.
from jobsapp.mixins import EmployeeRequiredMixin
from resume_cv.forms import ResumeCvForm
from resume_cv.models import ResumeCvTemplate, ResumeCvCategory, ResumeCv
from resume_cv.utils import sanitize_html

logger = logging.getLogger(__name__)

class TemplateListView(ListView):
    """
    Get list of templates to create resume/cv
    """

    model = ResumeCvTemplate
    context_object_name = "templates"
    template_name = "resumes/templates.html"

    def get_queryset(self):
        queryset = self.model.objects.filter(active=True)
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        return queryset

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["categories"] = ResumeCvCategory.objects.all()
        return data


class ResumeCVCreateView(LoginRequiredMixin, EmployeeRequiredMixin, View):
    """
    Create resume/cv
    """

    form_class = ResumeCvForm

    def post(self, request):
        try:
            template_id = request.POST.get('template')
            name = request.POST.get('name')
            
            if not template_id or not name:
                return redirect(reverse_lazy("resume_cv:templates"))
            
            template = ResumeCvTemplate.objects.get(id=template_id)
            
            # Create the resume
            resume = ResumeCv.objects.create(
                user=request.user,
                template=template,
                name=name,
                content=template.content,
                style=template.style
            )
            
            return redirect(reverse_lazy("resume_cv:builder", kwargs={"code": resume.code}))
        except (ResumeCvTemplate.DoesNotExist, Exception) as e:
            print(f"Error creating resume: {str(e)}")
            return redirect(reverse_lazy("resume_cv:templates"))


@method_decorator(login_required, name='dispatch')
class UserResumeListView(ListView):
    model = ResumeCv
    template_name = "resumes/list.html"
    context_object_name = "resumes"

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)


@login_required
@require_http_methods(["GET"])
@ratelimit(key='user', rate='30/m')
def resume_builder(request, code):
    """
    Render the resume builder interface
    """
    try:
        resume = get_object_or_404(ResumeCv, code=code)
        
        if resume.user != request.user:
            raise PermissionDenied("You don't have permission to access this resume")
            
        templates = ResumeCvTemplate.objects.filter(active=True)
        
        return render(request, "resumes/builder.html", {
            "resume": resume,
            "templates": templates
        })
    except Exception as e:
        logger.error(f"Error in resume_builder view: {str(e)}")
        return render(request, "error.html", {
            "message": "An error occurred while loading the resume builder"
        }, status=500)


@login_required
@require_http_methods(["POST"])
@ratelimit(key='user', rate='30/m')
def update_builder(request, id):
    """
    Update resume content and style
    """
    try:
        resume = get_object_or_404(ResumeCv, id=id)
        
        if resume.user != request.user:
            raise PermissionDenied("You don't have permission to modify this resume")
            
        data = json.loads(request.body)
        
        with transaction.atomic():
            resume.content = sanitize_html(data.get('gjs-html', ''))
            resume.style = data.get('gjs-css', '')
            resume.components = data.get('gjs-components', '[]')
            resume.assets = data.get('gjs-assets', '[]')
            resume.save()
            
        return JsonResponse({"status": "success"})
    except json.JSONDecodeError:
        logger.error("Invalid JSON in update_builder request")
        return JsonResponse({"error": "Invalid JSON data"}, status=400)
    except Exception as e:
        logger.error(f"Error in update_builder view: {str(e)}")
        return JsonResponse({"error": "Failed to update resume"}, status=500)


@login_required
@require_http_methods(["GET"])
@ratelimit(key='user', rate='30/m')
def load_builder(request, id):
    """
    Load resume content and style
    """
    try:
        resume = get_object_or_404(ResumeCv, id=id)
        
        if resume.user != request.user:
            raise PermissionDenied("You don't have permission to access this resume")
            
        return JsonResponse({
            'gjs-html': resume.content,
            'gjs-css': resume.style,
            'gjs-components': resume.components,
            'gjs-assets': resume.assets
        })
    except Exception as e:
        logger.error(f"Error in load_builder view: {str(e)}")
        return JsonResponse({"error": "Failed to load resume"}, status=500)


@login_required
@require_http_methods(["GET"])
@ratelimit(key='user', rate='30/m')
def load_template(request, id):
    """
    Load template content and style
    """
    try:
        template = get_object_or_404(ResumeCvTemplate, id=id)
        
        if not template.active:
            return JsonResponse({"error": "Template is not available"}, status=404)
            
        return JsonResponse({
            'content': template.content,
            'style': template.style
        })
    except Exception as e:
        logger.error(f"Error in load_template view: {str(e)}")
        return JsonResponse({"error": "Failed to load template"}, status=500)


@xframe_options_deny
@login_required
@user_is_employee
def download_resume(request, id):
    """
    Generate and download resume as PDF
    """
    try:
        resume = get_object_or_404(ResumeCv, id=id)
        
        if resume.user != request.user:
            raise PermissionDenied("You don't have permission to download this resume")
            
        # Combine HTML content with styles
        html_content = f"""
            <html>
                <head>
                    <style>{resume.style}</style>
                </head>
                <body>{resume.content}</body>
            </html>
        """
        
        # Generate PDF
        pdf = HTML(string=html_content).write_pdf()
        
        # Create response
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="resume_{resume.code}.pdf"'
        
        return response
    except Exception as e:
        logger.error(f"Error in download_resume view: {str(e)}")
        return JsonResponse({"error": "Failed to generate PDF"}, status=500)


@login_required
@user_is_employee
def download_template(request, id):
    template = ResumeCvTemplate.objects.get(id=id)
    if template:
        font_config = FontConfiguration()
        css = CSS(
            string=template.style,
            font_config=font_config,
        )
        pdf_file = HTML(string=template.content, encoding="utf-8").write_pdf(stylesheets=[css], font_config=font_config)
        response = HttpResponse(pdf_file, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{template.name}.pdf"'
        return response
    return redirect("resume_cv:templates")
