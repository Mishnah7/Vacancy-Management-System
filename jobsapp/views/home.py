from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect, JsonResponse, HttpResponseNotAllowed
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, DetailView, ListView, TemplateView
from django.core.cache import cache
from django.db.models import Q

from ..decorators import user_is_employee
from ..forms import ApplyJobForm, ContactForm
from ..models import Applicant, Favorite, Job, EmployeeProfile


class AboutView(TemplateView):
    template_name = 'jobs/about.html'


class FAQView(TemplateView):
    template_name = "jobs/faq.html"


class SupportView(TemplateView):
    template_name = "jobs/support.html"


class ContactView(CreateView):
    template_name = "jobs/contact.html"
    form_class = ContactForm
    success_url = reverse_lazy('jobs:contact')

    def form_valid(self, form):
        messages.success(self.request, "Your message has been sent successfully!")
        return super().form_valid(form)


class HomeView(ListView):
    model = Job
    template_name = "home.html"
    context_object_name = "jobs"

    def get_queryset(self):
        base_queryset = self.model.objects.filter(
            last_date__gte=timezone.now()
        ).select_related(
            'user'
        ).prefetch_related(
            'tags', 'applicants'
        )

        # If user is authenticated
        if self.request.user.is_authenticated:
            if self.request.user.role == 'employer':
                # Employers can see all jobs
                return base_queryset[:6]
            try:
                # Check if internal employee
                EmployeeProfile.objects.get(user=self.request.user)
                return base_queryset.filter(posting_type__in=['internal', 'both'])[:6]
            except EmployeeProfile.DoesNotExist:
                # External users see external and both
                return base_queryset.filter(posting_type__in=['external', 'both'])[:6]
        
        # Unauthenticated users see only external
        return base_queryset.filter(posting_type='external')[:6]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        base_queryset = self.model.objects.filter(
            last_date__gte=timezone.now(),
            created_at__month=timezone.now().month
        ).select_related('user').prefetch_related('tags')

        if self.request.user.is_authenticated:
            if self.request.user.role == 'employer':
                trending_jobs = base_queryset[:3]
            else:
                try:
                    EmployeeProfile.objects.get(user=self.request.user)
                    trending_jobs = base_queryset.filter(posting_type__in=['internal', 'both'])[:3]
                except EmployeeProfile.DoesNotExist:
                    trending_jobs = base_queryset.filter(posting_type__in=['external', 'both'])[:3]
        else:
            trending_jobs = base_queryset.filter(posting_type='external')[:3]

        context["trendings"] = cache.get_or_set(
            'trending_jobs',
            trending_jobs,
            3600  # 1 hour cache
        )
        return context


class SearchView(ListView):
    model = Job
    template_name = "jobs/search.html"
    context_object_name = "jobs"
    paginate_by = 10

    def get_queryset(self):
        base_queryset = self.model.objects.filter(
            last_date__gte=timezone.now()
        ).order_by('-created_at')
        
        # Get search parameters
        position = self.request.GET.get("q", "").strip()
        location = self.request.GET.get("l", "").strip()
        
        # Apply search filters
        if position:
            base_queryset = base_queryset.filter(
                Q(title__icontains=position) |
                Q(description__icontains=position) |
                Q(company_name__icontains=position)
            )
        if location:
            base_queryset = base_queryset.filter(location__icontains=location)
        
        # Filter based on user type (internal/external)
        if self.request.user.is_authenticated:
            if self.request.user.role == 'employer':
                return base_queryset
            try:
                employee = EmployeeProfile.objects.get(user=self.request.user)
                # Internal employees can see internal and both types
                return base_queryset.filter(posting_type__in=['internal', 'both'])
            except EmployeeProfile.DoesNotExist:
                # External users can see external and both types
                return base_queryset.filter(posting_type__in=['external', 'both'])
        else:
            # Unauthenticated users can only see external postings
            return base_queryset.filter(posting_type='external')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "")
        context["l"] = self.request.GET.get("l", "")
        context["total_jobs"] = self.get_queryset().count()
        return context


class JobListView(ListView):
    model = Job
    template_name = "jobs/jobs.html"
    context_object_name = "jobs"
    paginate_by = 5

    def get_queryset(self):
        base_queryset = self.model.objects.filter(
            last_date__gte=timezone.now()
        ).order_by('-created_at')

        # Get search parameters
        search_query = self.request.GET.get('search', '').strip()
        
        # Apply search if query exists
        if search_query:
            base_queryset = base_queryset.filter(
                Q(title__icontains=search_query) |
                Q(location__icontains=search_query) |
                Q(company_name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
            
        # If user is authenticated
        if self.request.user.is_authenticated:
            if self.request.user.role == 'employer':
                # Employers can see all jobs
                return base_queryset
            try:
                # Check if internal employee
                EmployeeProfile.objects.get(user=self.request.user)
                return base_queryset.filter(posting_type__in=['internal', 'both'])
            except EmployeeProfile.DoesNotExist:
                # External users see external and both
                return base_queryset.filter(posting_type__in=['external', 'both'])
        
        # Unauthenticated users see only external
        return base_queryset.filter(posting_type='external')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_jobs"] = self.get_queryset().count()
        context["search_query"] = self.request.GET.get('search', '')
        return context


class JobDetailsView(DetailView):
    model = Job
    template_name = "jobs/details.html"
    context_object_name = "job"
    pk_url_kwarg = "id"

    def get_object(self, queryset=None):
        try:
            obj = super(JobDetailsView, self).get_object(queryset=queryset)
            if obj is None:
                raise Http404("Job doesn't exist")
            return obj
        except:
            raise Http404("Job doesn't exist")

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            # Check if the job is internal only and user is not an internal employee
            if self.object.posting_type == 'internal':
                if not request.user.is_authenticated:
                    messages.error(request, "This job posting is for internal employees only.")
                    return HttpResponseRedirect(reverse_lazy("jobs:home"))
                try:
                    employee = EmployeeProfile.objects.get(user=request.user)
                except EmployeeProfile.DoesNotExist:
                    messages.error(request, "This job posting is for internal employees only.")
                    return HttpResponseRedirect(reverse_lazy("jobs:home"))
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)
        except Http404:
            messages.error(request, "Job doesn't exist")
            return HttpResponseRedirect(reverse_lazy("jobs:home"))


class ApplyJobView(CreateView):
    model = Applicant
    form_class = ApplyJobForm
    slug_field = "job_id"
    slug_url_kwarg = "job_id"

    @method_decorator(login_required(login_url=reverse_lazy("accounts:login")))
    @method_decorator(user_is_employee)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(self.request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(self._allowed_methods())

    def post(self, request, *args, **kwargs):
        try:
            form = self.get_form()
            if form.is_valid():
                messages.info(self.request, "Successfully applied for the job!")
                return self.form_valid(form)
            else:
                messages.error(self.request, "There was an error with your application.")
                return HttpResponseRedirect(reverse_lazy("jobs:home"))
        except:
            messages.error(self.request, "There was an error with your application.")
            return HttpResponseRedirect(reverse_lazy("jobs:home"))

    def get_success_url(self):
        return reverse_lazy("jobs:jobs-detail", kwargs={"id": self.kwargs["job_id"]})

    def form_valid(self, form):
        try:
            # Get the job
            job = Job.objects.get(id=self.kwargs["job_id"])
            
            # Check if the job is internal only
            if job.posting_type == 'internal':
                try:
                    employee = EmployeeProfile.objects.get(user=self.request.user)
                except EmployeeProfile.DoesNotExist:
                    messages.error(self.request, "This job posting is for internal employees only.")
                    return HttpResponseRedirect(self.get_success_url())

            # Check if user already applied
            applicant = Applicant.objects.filter(user_id=self.request.user.id, job_id=self.kwargs["job_id"])
            if applicant:
                messages.info(self.request, "You already applied for this job")
                return HttpResponseRedirect(self.get_success_url())
            
            # Save applicant
            form.instance.user = self.request.user
            form.instance.job = job
            form.save()
            return super().form_valid(form)
        except Job.DoesNotExist:
            messages.error(self.request, "Job doesn't exist")
            return HttpResponseRedirect(reverse_lazy("jobs:home"))
        except:
            messages.error(self.request, "There was an error with your application.")
            return HttpResponseRedirect(reverse_lazy("jobs:home"))


def favorite(request):
    if not request.user.is_authenticated:
        return JsonResponse(data={"auth": False, "status": "error"})

    job_id = request.POST.get("job_id")
    user_id = request.user.id
    try:
        favorite = Favorite.objects.get(job_id=job_id, user_id=user_id)
        favorite.delete()
        return JsonResponse(
            data={"auth": True, "status": "removed", "message": "Job removed from your favorite list"}
        )
    except Favorite.DoesNotExist:
        Favorite.objects.create(job_id=job_id, user_id=user_id)
        return JsonResponse(data={"auth": True, "status": "added", "message": "Job added to your favorite list"})
