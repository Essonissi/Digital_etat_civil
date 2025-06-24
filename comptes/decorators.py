from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from functools import wraps

def role_required(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if user.is_authenticated and user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            if not user.is_authenticated:
                return redirect('login')  # ou vers ta page de login
            return HttpResponseForbidden("Accès interdit")
        return _wrapped_view
    return decorator
