from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

from jobsapp.views import EditProfileView, EmployerProfileEditView
from .views import *

app_name = "accounts"

urlpatterns = [
    path("employee/register/", RegisterEmployeeView.as_view(), name="employee-register"),
    path("employer/register/", RegisterEmployerView.as_view(), name="employer-register"),
    path("employee/profile/update/", EditProfileView.as_view(), name="employee-profile-update"),
    path("employer/profile/update/", EmployerProfileEditView.as_view(), name="employer-profile-update"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("login/", CustomLoginView.as_view(), name="login"),
    # Password reset URLs
    path("password-reset/", 
         auth_views.PasswordResetView.as_view(
             template_name="accounts/password_reset.html",
             subject_template_name="accounts/password_reset_subject.txt",
             email_template_name="accounts/password_reset_email.html",
             success_url=reverse_lazy("accounts:password_reset_done")
         ), 
         name="password_reset"),
    path("password-reset/done/", 
         auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_done.html"), 
         name="password_reset_done"),
    path("password-reset-confirm/<uidb64>/<token>/", 
         auth_views.PasswordResetConfirmView.as_view(
             template_name="accounts/password_reset_confirm.html",
             success_url=reverse_lazy("accounts:password_reset_complete")
         ), 
         name="password_reset_confirm"),
    path("password-reset-complete/", 
         auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_complete.html"), 
         name="password_reset_complete"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
