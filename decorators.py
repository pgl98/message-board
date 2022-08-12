from flask import redirect, url_for, g, request, abort
from functools import wraps

def login_required(view):
    @wraps(view)
    def decorated_function(**kwargs):
        if g.user is None:
            return redirect( url_for('auth.login', next=request.url) )
            # The <next> value will exist in <request.args> after a GET request for the login page
        return view(**kwargs)
    return decorated_function

def admin_required(view):
    @wraps(view)
    def decorated_function(**kwargs):
        # to access the page, the user must be logged in and be an admin.
        if g.user is None or g.is_admin == False:
            return abort(401)
        return view(**kwargs)
    return decorated_function