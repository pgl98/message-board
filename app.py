from flask import Flask, render_template, redirect, url_for, session, g, request
from flask_session import Session
from functools import wraps
from forms import ThreadForm, RegisterForm, LoginForm, CommentForm, DeleteForm
from database import get_db, close_db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "this-is-my-secret-key"
app.teardown_appcontext(close_db)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# DELETE THIS BEFORE SUBMITTING
@app.before_first_request
def init_db():
    db = get_db()
    try:
        print("hello")
        pw_hash = generate_password_hash("internetjanitor")
        db.execute("""
            INSERT INTO users
            VALUES ("admin", ?, TRUE);
        """, (pw_hash,))
        db.commit()
    except:
        print("admin already in database")

#

@app.before_request
# registers this function to run before each request,
# so that if the user is logged in, their username is stored in session
def load_logged_in_user():
    g.user = session.get("username", None)

def login_required(view):
    @wraps(view)
    def decorated_function(**kwargs):
        if g.user is None:
            return redirect( url_for('login', next=request.url) )
            # The <next> value will exist in <request.args> after a GET request for the login page
        return view(**kwargs)
    return decorated_function


@app.route("/", methods=["GET", "POST"])
def index():
    db = get_db()

    threads = db.execute("""
        SELECT * FROM threads;
    """).fetchall()

    return render_template("index.html", threads=threads)

@app.route("/thread/<int:thread_id>", methods=["GET", "POST"])
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
        username = session["username"]
        date_created = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        
        db.execute("""
            INSERT INTO comments (thread_id, username, date_created, body)
            VALUES (?, ?, ?, ?);
        """, (thread_id, username, date_created, body,))
        db.commit()

        return redirect(url_for("thread", thread_id=thread_id))

    comments = db.execute("""
        SELECT * FROM comments
        WHERE thread_id = ?;
    """, (thread_id,)).fetchall()

    return render_template("thread.html", thread=thread, comments=comments, form=form)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    message = None

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        db = get_db()

        usernames = db.execute("""
            SELECT username FROM users;
        """).fetchall()

        print(usernames)

        # if username is already registered, the try block will give an error
        # since username is the primary key of the users table
        try:
            db.execute("""
                INSERT INTO users
                VALUES (?, ?, ?);
            """, (username, generate_password_hash(password)), False,)
            db.commit()

            message = "Successful Registration"

            return redirect("login")
        except:
            # For now, force user to put in password again. May change later.
            # let them see the taken username, though.
            form.password.data = None
            message = "Username already taken. Try another one."

    return render_template("register.html", form=form, message=message)

@app.route("/login", methods=["GET", "POST"])
def login(message:str=None):
    form = LoginForm()
    username = None
    password = None

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        db = get_db()

        try:
            user = db.execute("""
            SELECT * FROM users
            WHERE username = ?;
            """, (username,)).fetchone()

            password_is_valid = check_password_hash(user["password_hash"], password)

            if user is not None and password_is_valid:
                message = "Successful log in!"
                session.clear()
                session["username"] = username

                # look at 'login_required' decorator
                next_page = request.args.get("next")
                if not next_page:
                    next_page = url_for("index")
                return redirect(next_page)
            else:
                message = "Invalid username or password"
        except:
            # don't specify which of the username or password is wrong for better security
            message = "Invalid username or password"

    return render_template("login.html", form=form, message=message)

#------- ROUTES FOR LOGGED-IN USERS ONLY ----------------

@app.route("/logout")
def logout():
    session.clear()

    return redirect("login")

@app.route("/post_thread", methods=["GET", "POST"])
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

        return redirect("/")
    
    return render_template("thread_form.html", form=form)

@app.route("/delete_thread", methods=["POST"])
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

    return redirect("/")

@app.route("/delete_comment/", methods=["POST"])
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

    return redirect(url_for("thread", thread_id=thread_id))
