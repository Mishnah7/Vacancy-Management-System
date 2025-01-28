from django.urls import include, path
from .views import AboutView, FAQView, SupportView, ContactView, jobs
from .views.home import HomeView, SearchView, JobListView, JobDetailsView, ApplyJobView, favorite
from .views.employer import (
    DashboardView, ApplicantsListView, ApplicantPerJobView, 
    AppliedApplicantView, filled, SendResponseView, 
    JobCreateView, JobUpdateView
)
from .views.employee import EmployeeMyJobsListView, FavoriteListView

app_name = "jobs"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("about/", AboutView.as_view(), name="about"),
    path("faq/", FAQView.as_view(), name="faq"),
    path("support/", SupportView.as_view(), name="support"),
    path("contact/", ContactView.as_view(), name="contact"),
    path("favorite/", favorite, name="favorite"),
    path("search/", SearchView.as_view(), name="search"),
    path(
        "employer/dashboard/",
        include(
            [
                path("", DashboardView.as_view(), name="employer-dashboard"),
                path("all-applicants/", ApplicantsListView.as_view(), name="employer-all-applicants"),
                path("applicants/<int:job_id>/", ApplicantPerJobView.as_view(), name="employer-dashboard-applicants"),
                path(
                    "applied-applicant/<int:job_id>/view/<int:applicant_id>",
                    AppliedApplicantView.as_view(),
                    name="applied-applicant-view",
                ),
                path("mark-filled/<int:job_id>/", filled, name="job-mark-filled"),
                path("send-response/<int:applicant_id>", SendResponseView.as_view(), name="applicant-send-response"),
                path("jobs/create/", JobCreateView.as_view(), name="employer-jobs-create"),
                path("jobs/<int:id>/edit/", JobUpdateView.as_view(), name="employer-jobs-edit"),
            ]
        ),
    ),
    path(
        "employee/",
        include(
            [
                path("my-applications", EmployeeMyJobsListView.as_view(), name="employee-my-applications"),
                path("favorites", FavoriteListView.as_view(), name="employee-favorites"),
            ]
        ),
    ),
    path("apply-job/<int:job_id>/", ApplyJobView.as_view(), name="apply-job"),
    path("jobs/", JobListView.as_view(), name="jobs"),
    path("jobs/<int:id>/", JobDetailsView.as_view(), name="jobs-detail"),
    # Resume builder URLs
    path("resume/", include("resume_cv.urls", namespace="resume_cv")),
    path('favorite/', jobs.toggle_favorite, name='favorite'),
]
