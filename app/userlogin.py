from app import app
from flask_login import current_user
from functools import wraps


def role_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):

            if current_user.is_authenticated:
                if role == 'ANY' or [x for x in current_user.roles if x.name == role]:
                    return fn(*args, **kwargs)
            return app.login_manager.unauthorized()
        return decorated_view
    return wrapper
