from threading import local

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