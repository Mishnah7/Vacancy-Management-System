from django.contrib import auth, messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, RedirectView
from django.contrib.auth.views import LoginView
from django.forms.models import model_to_dict
from jobsapp.models import Audit
from jobsapp.signals import get_client_ip

from accounts.forms import *
from accounts.models import User


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = UserLoginForm
    
    def form_valid(self, form):
        auth.login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
            
        user = self.request.user
        if user.is_authenticated:
            if user.role == 'admin':
                return reverse_lazy('admin:index')
            elif user.role == 'employer':
                return reverse_lazy('jobs:employer-dashboard')
            else:  # employee
                return reverse_lazy('jobs:home')
        return reverse_lazy('accounts:login')


class RegisterEmployeeView(CreateView):
    model = User
    form_class = EmployeeRegistrationForm
    template_name = "accounts/employee/register.html"
    success_url = "/"

    extra_context = {"title": "Register"}

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.success_url)
        return super().dispatch(self.request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)

        if form.is_valid():
            user = form.save()
            # Create audit log for user registration
            Audit.objects.create(
                user=None,  # No user yet since this is registration
                action='INSERT',
                table_name='user',
                record_id=user.id,
                new_values={
                    'username': user.username,
                    'email': user.email,
                    'role': 'employee',
                    'registration_type': 'Employee Registration'
                },
                ip_address=get_client_ip(request)
            )
            return redirect("accounts:login")
        else:
            return render(request, "accounts/employee/register.html", {"form": form})


class RegisterEmployerView(CreateView):
    model = User
    form_class = EmployerRegistrationForm
    template_name = "accounts/employer/register.html"
    success_url = "/"

    extra_context = {"title": "Register"}

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(self.success_url)
        return super().dispatch(self.request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)

        if form.is_valid():
            user = form.save()
            # Create audit log for user registration
            Audit.objects.create(
                user=None,  # No user yet since this is registration
                action='INSERT',
                table_name='user',
                record_id=user.id,
                new_values={
                    'username': user.username,
                    'email': user.email,
                    'role': 'employer',
                    'registration_type': 'Employer Registration'
                },
                ip_address=get_client_ip(request)
            )
            return redirect("accounts:login")
        else:
            return render(request, "accounts/employer/register.html", {"form": form})


class LogoutView(RedirectView):
    """
    Provides users the ability to logout
    """

    url = '/login/'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            # Create audit log for logout
            Audit.objects.create(
                user=request.user,
                action='UPDATE',
                table_name='user',
                record_id=request.user.id,
                new_values={
                    'event': 'User Logout',
                    'username': request.user.username
                },
                ip_address=get_client_ip(request)
            )
        auth.logout(request)
        messages.success(request, 'You are now logged out')
        return super(LogoutView, self).get(request, *args, **kwargs)
