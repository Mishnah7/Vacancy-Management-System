from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from django.utils import timezone
from django.db.models import Count, Q
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
import bleach
from django.core.exceptions import ValidationError

from accounts.forms import EmployerProfileUpdateForm
from jobsapp.decorators import user_is_employer
from jobsapp.forms import CreateJobForm
from jobsapp.models import Applicant, Job
from tags.models import Tag


def sanitize_html(html_content):
    """
    Sanitize HTML content to prevent XSS attacks while preserving safe HTML tags
    """
    allowed_tags = [
        'p', 'br', 'strong', 'b', 'i', 'em', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'table', 'tr', 'td', 'th', 'thead', 'tbody', 'a', 'span', 'div'
    ]
    allowed_attributes = {
        'a': ['href', 'title', 'target'],
        'span': ['class'],
        'div': ['class'],
        '*': ['class']
    }
    
    clean_content = bleach.clean(
        html_content,
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True
    )
    return mark_safe(clean_content)


class DashboardView(ListView):
    model = Job
    template_name = "jobs/employer/dashboard.html"
    context_object_name = "jobs"
    paginate_by = 10

    @method_decorator(login_required(login_url=reverse_lazy("accounts:login")))
    @method_decorator(user_is_employer)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(self.request, *args, **kwargs)

    def get_queryset(self):
        # Show all jobs, ordered by creation date
        return self.model.objects.filter(user_id=self.request.user.id).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add today's date for template comparison
        today = timezone.now()
        context['today'] = today
        
        # Get user's own jobs
        user_jobs = self.model.objects.filter(user_id=self.request.user.id)
        context['own_jobs'] = user_jobs
        
        # Active Jobs Count (not filled and not expired)
        context['active_jobs_count'] = user_jobs.filter(
            filled=False,
            last_date__gte=today
        ).count()

        # Total Applicants
        context['total_applicants'] = Applicant.objects.filter(
            job__user_id=self.request.user.id
        ).count()

        # Filled Jobs Count
        context['filled_jobs_count'] = user_jobs.filter(filled=True).count()

        # Pending Reviews (applications not yet reviewed)
        context['pending_reviews'] = Applicant.objects.filter(
            job__user_id=self.request.user.id,
            status=1  # 1 represents pending status
        ).count()

        return context


class ApplicantPerJobView(ListView):
    model = Applicant
    template_name = "jobs/employer/applicants.html"
    context_object_name = "applicants"
    paginate_by = 6

    @method_decorator(login_required(login_url=reverse_lazy("accounts:login")))
    @method_decorator(user_is_employer)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(self.request, *args, **kwargs)

    def get_queryset(self):
        return Applicant.objects.filter(job_id=self.kwargs["job_id"]).order_by("id")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["job"] = Job.objects.get(id=self.kwargs["job_id"])
        return context


class JobCreateView(CreateView):
    template_name = "jobs/create.html"
    form_class = CreateJobForm
    extra_context = {"title": "Post New Job"}
    success_url = reverse_lazy("jobs:employer-dashboard")

    @method_decorator(login_required(login_url=reverse_lazy("accounts:login")))
    @method_decorator(user_is_employer)
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy("accounts:login"))
        if self.request.user.is_authenticated and self.request.user.role != "employer":
            return HttpResponseRedirect(reverse_lazy("accounts:login"))
        return super().dispatch(self.request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tags"] = Tag.objects.all()
        return context

    def form_valid(self, form):
        try:
            form.instance.user = self.request.user
            # Clean and sanitize HTML content
            if form.cleaned_data.get('description'):
                form.instance.description = sanitize_html(form.cleaned_data['description'])
            if form.cleaned_data.get('company_description'):
                form.instance.company_description = sanitize_html(form.cleaned_data['company_description'])
            
            response = super().form_valid(form)
            messages.success(self.request, "Job position created successfully!")
            return response
        except Exception as e:
            messages.error(self.request, f"An error occurred: {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        try:
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        except ValidationError as e:
            messages.error(self.request, str(e))
            return self.render_to_response(self.get_context_data(form=form))
        except Exception as e:
            messages.error(self.request, "An unexpected error occurred while creating the job position. Please try again.")
            return self.render_to_response(self.get_context_data(form=form))


@method_decorator(login_required(login_url=reverse_lazy("accounts:login")), name="dispatch")
@method_decorator(user_is_employer, name="dispatch")
class JobUpdateView(UpdateView):
    template_name = "jobs/update.html"
    form_class = CreateJobForm
    extra_context = {"title": "Edit Job"}
    slug_field = "id"
    slug_url_kwarg = "id"
    success_url = reverse_lazy("jobs:employer-dashboard")
    context_object_name = "job"

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(self.request, *args, **kwargs)

    def get_queryset(self):
        return Job.objects.filter(user_id=self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tags"] = Tag.objects.all()
        context['today'] = timezone.now().date()  # Add today's date for expiration check
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        
        # Clean and sanitize HTML content
        if form.cleaned_data.get('description'):
            form.instance.description = sanitize_html(form.cleaned_data['description'])
        
        if form.cleaned_data.get('company_description'):
            form.instance.company_description = sanitize_html(form.cleaned_data['company_description'])
        
        messages.success(self.request, "Job updated successfully")
        return super(JobUpdateView, self).form_valid(form)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class ApplicantsListView(ListView):
    model = Applicant
    template_name = "jobs/employer/all-applicants.html"
    context_object_name = "applicants"

    @method_decorator(login_required(login_url=reverse_lazy("accounts:login")))
    @method_decorator(user_is_employer)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(self.request, *args, **kwargs)

    def get_queryset(self):
        # jobs = Job.objects.filter(user_id=self.request.user.id)
        # return self.model.objects.filter(job__user_id=self.request.user.id)
        self.queryset = self.model.objects.filter(job__user_id=self.request.user.id).order_by("id")
        if "status" in self.request.GET and len(self.request.GET.get("status")) > 0:
            self.queryset = self.queryset.filter(status=int(self.request.GET.get("status")))
        return self.queryset


@login_required(login_url=reverse_lazy("accounts:login"))
@user_is_employer
def filled(request, job_id=None):
    try:
        job = Job.objects.get(user_id=request.user.id, id=job_id)
        job.filled = True
        job.save()
    except IntegrityError as e:
        return HttpResponseRedirect(reverse_lazy("jobs:employer-dashboard"))
    return HttpResponseRedirect(reverse_lazy("jobs:employer-dashboard"))


@method_decorator(login_required(login_url=reverse_lazy("accounts:login")), name="dispatch")
@method_decorator(user_is_employer, name="dispatch")
class AppliedApplicantView(DetailView):
    model = Applicant
    template_name = "jobs/employer/applied-applicant-view.html"
    context_object_name = "applicant"
    slug_field = "id"
    slug_url_kwarg = "applicant_id"

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(self.request, *args, **kwargs)

    def get_queryset(self):
        return Applicant.objects.select_related("job").filter(job_id=self.kwargs["job_id"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


@method_decorator(login_required(login_url=reverse_lazy("accounts:login")), name="dispatch")
@method_decorator(user_is_employer, name="dispatch")
class SendResponseView(UpdateView):
    model = Applicant
    http_method_names = ["post"]
    pk_url_kwarg = "applicant_id"
    fields = ("status", "comment")

    def get_success_url(self):
        return reverse_lazy(
            "jobs:applied-applicant-view",
            kwargs={"job_id": self.request.POST.get("job_id"), "applicant_id": self.get_object().id},
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.status != request.POST.get("status"):
            if request.POST.get("status") == "1":
                status = "Pending"
            elif request.POST.get("status") == "2":
                status = "Accepted"
            else:
                status = "Rejected"
            messages.success(self.request, "Response was successfully sent")
            # notify_candidate_about_job_status_change.delay(self.object.user.get_full_name(),
            # self.object.user.email, self.object.job.id, self.object.job.title, status)
        else:
            messages.warning(self.request, "Response already sent")
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()
        pk = self.kwargs.get(self.pk_url_kwarg)
        queryset = queryset.filter(pk=pk)
        try:
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(
                "No %(verbose_name)s found matching the query" % {"verbose_name": queryset.model._meta.verbose_name}
            )
        return obj


class EmployerProfileEditView(UpdateView):
    form_class = EmployerProfileUpdateForm
    context_object_name = "employer"
    template_name = "jobs/employer/edit-profile.html"
    success_url = reverse_lazy("accounts:employer-profile-update")

    @method_decorator(login_required(login_url=reverse_lazy("accounts:login")))
    @method_decorator(user_is_employer)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(self.request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except Http404:
            raise Http404("User doesn't exists")
        return self.render_to_response(self.get_context_data())

    def get_object(self, queryset=None):
        obj = self.request.user
        if obj is None:
            raise Http404("Job doesn't exists")
        return obj
