from threading import local
from django.conf import settings
from django.contrib import auth
from django.contrib.auth import logout
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import redirect
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

_thread_locals = local()

class RequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        response = self.get_response(request)
        return response

    @staticmethod
    def get_request():
        return getattr(_thread_locals, 'request', None)

class SessionTimeoutMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if not hasattr(request, 'user'):
            return None
            
        if not request.user.is_authenticated:
            return None

        try:
            current_time = timezone.now()
            last_activity = request.session.get('last_activity')
            
            if last_activity:
                last_activity = timezone.datetime.fromisoformat(last_activity)
                
                if hasattr(settings, 'SESSION_IDLE_TIMEOUT'):
                    idle_timeout = getattr(settings, 'SESSION_IDLE_TIMEOUT', 1800)  # Default 30 minutes
                    if current_time > last_activity + timedelta(seconds=idle_timeout):
                        logout(request)
                        logger.info(f"User {request.user} logged out due to inactivity")
                        return redirect(settings.LOGIN_URL)
            
            request.session['last_activity'] = current_time.isoformat()
            
        except Exception as e:
            logger.error(f"Error in SessionTimeoutMiddleware: {str(e)}")
            return None 