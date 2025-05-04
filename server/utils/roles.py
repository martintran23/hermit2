# server/utils/roles.py

from functools import wraps
from flask import session, jsonify

def role_required(*allowed_roles):
    """
    Decorator to restrict access to routes based on session['role'].
    Usage: @role_required('host') or @role_required('traveler','host')
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            role = session.get('role')
            if role not in allowed_roles:
                return jsonify({"error": "Forbidden"}), 403
            return f(*args, **kwargs)
        return wrapped
    return decorator
