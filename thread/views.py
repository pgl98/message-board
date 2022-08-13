from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, request, session

from database import get_db
from decorators import login_required
from forms import CommentForm

thread_bp = Blueprint('thread', __name__, template_folder='../thread/templates/thread')

@thread_bp.route("/")
def index():
    db = get_db()

    threads = db.execute("""
        SELECT * FROM threads;
    """).fetchall()

    return render_template("index.html", threads=threads)


@thread_bp.route("/thread/<int:thread_id>", methods=["GET", "POST"])
def thread(thread_id):
    form = CommentForm()

    db = get_db()
    thread = db.execute("""
        SELECT * FROM threads
        WHERE thread_id = ?;
    """, (thread_id,)).fetchone()

    # This is the only endpoint in which a user can post comments,
    # so I decided to leave the CommentForm here, (instead of making it its own route), even if it is messy.
    if form.validate_on_submit():
        body = form.body.data
        username = session['username']#
        date_created = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        
        db.execute("""
            INSERT INTO comments (thread_id, username, date_created, body)
            VALUES (?, ?, ?, ?);
        """, (thread_id, username, date_created, body,))
        db.commit()

        return redirect( url_for("thread.thread", thread_id=thread_id) )

    comments = db.execute("""
        SELECT * FROM comments
        WHERE thread_id = ?;
    """, (thread_id,)).fetchall()

    return render_template("thread.html", thread=thread, comments=comments, form=form)

@thread_bp.route("/delete_thread", methods=["POST"])
@login_required
def delete_thread():
    thread_id = int(request.form["thread_id"])
    db = get_db()

    db.execute("""
        DELETE FROM threads
        WHERE thread_id = ?;
    """, (thread_id,))

    db.execute("""
        DELETE FROM comments
        WHERE thread_id = ?;
    """, (thread_id,))

    db.commit()

    return redirect( url_for("thread.index") )

@thread_bp.route("/delete_comment/", methods=["POST"])
@login_required
def delete_comment():
    comment_id = int(request.form["comment_id"])
    thread_id = int(request.form["thread_id"])
    db = get_db()

    db.execute("""
        DELETE FROM comments
        WHERE comment_id = ?;
    """, (comment_id,))
    db.commit()

    return redirect( url_for("thread.thread", thread_id=thread_id) )