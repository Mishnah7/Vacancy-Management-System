from django.urls import path

from .views import (
    TemplateListView,
    ResumeCVCreateView,
    resume_builder,
    UserResumeListView,
    download_resume,
    update_builder,
    load_builder,
    load_template,
)

app_name = "resume_cv"

urlpatterns = [
    path("templates", TemplateListView.as_view(), name="templates"),
    path("resume-cv/create", ResumeCVCreateView.as_view(), name="create"),
    path("templates/builder/<str:code>", resume_builder, name="builder"),
    path("resumes/", UserResumeListView.as_view(), name="resumes"),
    path("download-as-pdf/<int:id>/", download_resume, name="export.pdf"),
    path("resume-cv/update/builder/<int:id>/", update_builder, name="resume-cv.update.builder"),
    path("resume-cv/load/builder/<int:id>/", load_builder, name="resume-cv.load.builder"),
    path("template/<int:id>/", load_template, name="load.template"),
]
