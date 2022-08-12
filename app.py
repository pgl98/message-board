import os
from flask import Flask, render_template, redirect, url_for, session, g, request, abort
from flask_session import Session
from functools import wraps
from forms import ThreadForm, RegisterForm, LoginForm, CommentForm, DeleteForm, UserProfileForm
from database import get_db, close_db
from werkzeug.security import generate_password_hash, check_password_hash
# this is to make uploading files more secure, see 'Information for the Pros' section here: https://flask.palletsprojects.com/en/2.0.x/patterns/fileuploads/
from werkzeug.utils import secure_filename
from datetime import datetime

from thread.views import thread_bp
from user.views import user_bp
from auth.views import auth_bp

from decorators import login_required, admin_required


app = Flask(__name__)
app.config["SECRET_KEY"] = "this-is-my-secret-key"
app.config["UPLOAD_FOLDER"] = 'static/uploads/'
app.teardown_appcontext(close_db)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"


app.register_blueprint(thread_bp)
app.register_blueprint(user_bp)
app.register_blueprint(auth_bp)

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




# @app.route("/edit_profile", methods=["POST"])
# @login_required
# def edit_profile():
#     form = UserProfileForm()
#     username = ""
#     filename = ""

#     # there are two ways to access this route:
#     #   i.  by submitting form in the 'user_list' route
#     #   ii. by submitting the form in this route

#     # if i., get the username from the request
#     try:
#         username = request.form["username"]
#         form.username.data = username
#     # if ii. get the username from the form
#     except:
#         username = form.id.data

#     if form.validate_on_submit():
#         new_profile_image = form.profile_image.data
#         about = form.about.data
#         db = get_db()

#         current_profile_image = db.execute("""
#             SELECT profile_image from users
#             WHERE username = ?;
#         """, (username,)).fetchone()["profile_image"]

#         # if the user has submitted a new profile image...
#         if new_profile_image:
#             # if the user already has a profile image, delete it
#             if current_profile_image:
#                 os.remove(os.path.join(
#                     app.config["UPLOAD_FOLDER"], current_profile_image
#                 ))

#             # all the code involved in uploading images is a modified version of the code found here :https://flask-wtf.readthedocs.io/en/latest/form/

#             # sanitize the name to prevent XSS (probably not necessary since the filename is changed anyway but it's no harm)
#             filename = secure_filename(new_profile_image.filename)
#             file_extension = os.path.splitext(filename)[1]

#             # the filename for the image will be of the form '<username>.<file extension>' because usernames are unique
#             filename = username + file_extension
#             # save the image to the the filepath returned by os.path.join().
#             new_profile_image.save(os.path.join(
#                 app.config["UPLOAD_FOLDER"], filename
#             ))
#         else:
#             filename = current_profile_image

#         db.execute("""
#             UPDATE users
#             SET about = ?, profile_image = ?
#             WHERE username = ?;
#         """, (about, filename, username,))
#         db.commit()

#         return redirect( url_for("user_profile", username=username) )

#     return render_template("edit_user_profile.html", form=form)

