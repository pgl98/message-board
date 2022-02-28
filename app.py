from flask import Flask, render_template, redirect, url_for, session
from flask_session import Session
from forms import ThreadForm, RegisterForm, LoginForm, CommentForm
from database import get_db, close_db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "this-is-my-secret-key"
app.teardown_appcontext(close_db)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
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

    comments = db.execute("""
        SELECT * FROM comments
        WHERE thread_id = ?;
    """, (thread_id,)).fetchall()

    if form.validate_on_submit():
        body = form.body.data
        username = "PLACEHOLDER USERNAME"
        date_created = "PLACEHOLDER DATE"
        
        db.execute("""
            INSERT INTO comments (thread_id, username, date_created, body)
            VALUES (?, ?, ?, ?);
        """, (thread_id, username, date_created, body,))

        db.commit()

        return redirect(url_for("thread", thread_id=thread_id))


    return render_template("thread.html", thread=thread, comments=comments, form=form)

@app.route("/post_thread", methods=["GET", "POST"])
def post_thread():
    form = ThreadForm()

    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        date_created = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        user_poster = "PLACEHOLDER"

        db = get_db()
        db.execute("""
            INSERT INTO threads (title, body, date_created, user_poster)
            VALUES (?, ?, ?, ?);
        """, (title, body, date_created, user_poster,))

        db.commit()

        return redirect("/")
    
    return render_template("thread_form.html", form=form)

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

        # if username is already registered, the next block will give an error
        # since username is the primary key of the users table
        try:
            db.execute("""
                INSERT INTO users VALUES
                (?, ?);
            """, (username, generate_password_hash(password)),)
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
def login():
    form = LoginForm()
    username = None
    password = None
    message = None

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        db = get_db()

        user = db.execute("""
            SELECT * FROM users
            WHERE username = ?;
        """, (username,)).fetchone()

        password_is_valid = check_password_hash(user["password"], password)

        if username is not None and password_is_valid:
            message = "Successful log in!"
            session.clear()
            session["username"] = username

            return redirect("/")
        else:
            message = "Invalid username or password"

    return render_template("login.html", form=form, message=message)