from functools import wraps
from flask import url_for, request, redirect, session
from app.services.model import users
import flask_login

access_levels = {
    "user": 0,
    "moderator": 1,
    "admin": 2
}


def requires_access_level(access_level):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = flask_login.current_user.get_id()

            for user_it in users:
                if user_it.id == user_id:
                    user = user_it

            if not user.role >= access_level:
                return redirect(url_for("leaf_synsets"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator