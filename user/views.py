import os
from flask import Blueprint, render_template, redirect, url_for, session, request, current_app
from datetime import datetime
from werkzeug.utils import secure_filename

from database import get_db
from forms import ThreadForm, DeleteForm, UserProfileForm
from decorators import login_required, admin_required

user_bp = Blueprint('user', __name__, template_folder='../user/templates/user')


@user_bp.route("/user/<username>")
def user_profile(username):
    db = get_db()
    user_info = db.execute("""
        SELECT username, date_created, about, profile_image FROM users
        WHERE username = ?;
    """, (username,)).fetchone()

    return render_template("user_profile.html", user_info=user_info)


@user_bp.route("/user/<username>/comments")
def user_comments(username):
    db = get_db()

    user_info = db.execute("""
        SELECT username, date_created, about, profile_image FROM users
        WHERE username = ?;
    """, (username,)).fetchone()

    comments = db.execute("""
        SELECT * FROM comments
        WHERE username = ?;
    """, (username,))

    return render_template("user_comments.html", user_info=user_info, comments=comments)


@user_bp.route("/user/<username>/threads")
def user_threads(username):
    db = get_db()

    user_info = db.execute("""
        SELECT username, date_created, about, profile_image FROM users
        WHERE username = ?;
    """, (username,)).fetchone()

    threads = db.execute("""
        SELECT * FROM threads
        WHERE user_poster = ?;
    """, (username,))

    return render_template("user_threads.html", user_info=user_info, threads=threads)


@user_bp.route("/post_thread", methods=["GET", "POST"])
@login_required
def post_thread():
    form = ThreadForm()

    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        date_created = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        user_poster = session["username"]

        db = get_db()
        db.execute("""
            INSERT INTO threads (title, body, date_created, user_poster)
            VALUES (?, ?, ?, ?);
        """, (title, body, date_created, user_poster,))

        db.commit()

        return redirect( url_for("thread.index") )
    
    return render_template("thread_form.html", form=form)


@user_bp.route("/user_list", methods=["GET", "POST"])
@admin_required
def user_list():
    db = get_db()

    user_list = db.execute("""
        SELECT username from users;
    """).fetchall()

    return render_template("user_list.html", user_list=user_list)

@user_bp.route("/edit_profile", methods=["POST"])
@login_required
def edit_profile():
    form = UserProfileForm()
    username = ""
    filename = ""

    # there are two ways to access this route:
    #   i.  by submitting form in the 'user_list' route
    #   ii. by submitting the form in this route

    # if i., get the username from the request
    try:
        username = request.form["username"]
        form.username.data = username
    # if ii. get the username from the form
    except:
        username = form.id.data

    if form.validate_on_submit():
        new_profile_image = form.profile_image.data
        about = form.about.data
        db = get_db()

        current_profile_image = db.execute("""
            SELECT profile_image from users
            WHERE username = ?;
        """, (username,)).fetchone()["profile_image"]

        # if the user has submitted a new profile image...
        if new_profile_image:
            # if the user already has a profile image, delete it
            if current_profile_image:
                os.remove(os.path.join(
                    current_app.config["UPLOAD_FOLDER"], current_profile_image
                ))

            # all the code involved in uploading images is a modified version of the code found here :https://flask-wtf.readthedocs.io/en/latest/form/

            # sanitize the name to prevent XSS (probably not necessary since the filename is changed anyway but it's no harm)
            filename = secure_filename(new_profile_image.filename)
            file_extension = os.path.splitext(filename)[1]

            # the filename for the image will be of the form '<username>.<file extension>' because usernames are unique
            filename = username + file_extension
            # save the image to the the filepath returned by os.path.join().
            new_profile_image.save(os.path.join(
                current_app.config["UPLOAD_FOLDER"], filename
            ))
        else:
            filename = current_profile_image

        db.execute("""
            UPDATE users
            SET about = ?, profile_image = ?
            WHERE username = ?;
        """, (about, filename, username,))
        db.commit()

        return redirect( url_for("user.user_profile", username=username) )

    return render_template("edit_user_profile.html", form=form)

@user_bp.route("/delete_user", methods=["POST"])
@admin_required
def delete_user():
    form = DeleteForm()

    # same reasoning as for 'edit_profile' above
    try:
        username = request.form["username"]
        form.id.data = username
    except:
        username = form.id.data

    if form.validate_on_submit():
        db = get_db()

        db.execute("""
            DELETE FROM threads
            WHERE user_poster = ?;
        """, (username,))

        profile_image = db.execute("""
            SELECT profile_image from users
            WHERE username = ?;
        """, (username,)).fetchone()["profile_image"]

        if profile_image:
            os.remove(os.path.join(
                current_app.config["UPLOAD_FOLDER"], profile_image
            ))

        db.execute("""
            DELETE FROM users
            WHERE username = ?;
        """, (username,))

        db.commit()

        return redirect( url_for("user.user_list") )

    return render_template("delete_user.html", form=form, username=username)