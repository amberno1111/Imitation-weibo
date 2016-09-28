# -*- coding: utf-8 -*-
from functools import wraps
from flask_login import current_user
from flask import abort
from app.models import Permission


def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorator_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(404)
            return f(*args, **kwargs)
        return decorator_function
    return decorator


def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)
