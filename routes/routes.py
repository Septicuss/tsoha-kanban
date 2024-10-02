from functools import wraps
from flask import render_template, request, redirect, session, make_response

import users
from users import user_exists
from app import app

# Decorator, used for routes that need authentication
def require_login(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        if not 'username' in session or not user_exists(session['username']):
            response = make_response(redirect('/login'))

            if 'HX-Request' in request.headers:
                response = make_response()
                response.headers['HX-Redirect'] = '/login'

            return response
        user = None
        user = users.get_user(session['username'])

        # Attach the user object to kwargs if the function expects it
        if 'user' in f.__code__.co_varnames:
            kwargs['user'] = user

        return f(*args, **kwargs)
    return decorator