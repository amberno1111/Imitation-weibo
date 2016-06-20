from functools import wraps
from flask_login import current_user
from flask import abort
from .models import Permission


def permission_required(permission):
    def decorator(function):
        @wraps(function)
        def decorate_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return function(*args, **kwargs)
        return decorate_function
    return decorator


def admin_required(f):
    return permission_required(Permission.ADMINISTRATOR)(f)
