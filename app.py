from flask import Flask, render_template, session, g
from flask_session import Session
from database import close_db

from thread.views import thread_bp
from user.views import user_bp
from auth.views import auth_bp
from api.views import api_bp


app = Flask(__name__)
app.config["SECRET_KEY"] = "this-is-my-secret-key"
app.config["UPLOAD_FOLDER"] = 'static/uploads/'
app.teardown_appcontext(close_db)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"


app.register_blueprint(thread_bp)
app.register_blueprint(user_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(api_bp, url_prefix='/api')

Session(app)

'''
There are two types of users - administrators and ordinary users.
Administrators can delete any thread, comment, or user.
Ordinary users can only delete their own threads or comments.
To log in as an admin:
    username : 'admin',
    password : 'internetjanitor'

Once you've registered, make sure to customize your profile by clicking on 'User Profile'!
Check out other people's profiles, too.
'''

@app.before_request
# registers this function to run before each request,
# so that if the user is logged in, their username is stored in session,
# and if the user is an admin, 
def load_logged_in_user():
    g.user = session.get("username", None)
    g.is_admin = session.get("is_admin", False)

#----- Custom Error Handling -----------#
# just do most common errors.
# code found here: https://flask.palletsprojects.com/en/2.0.x/errorhandling/#custom-error-pages
@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html", error_message=str(e)), 404

@app.errorhandler(401)
def unauthorized(e):
    return render_template("error.html", error_message=str(e)), 401

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("error.html", error_message=str(e)), 500
