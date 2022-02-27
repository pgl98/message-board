from flask import Flask, render_template, redirect
from forms import ThreadForm, RegisterForm, LoginForm
from database import get_db, close_db
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "this-is-my-secret-key"
app.teardown_appcontext(close_db)

@app.route("/")
def index():
    db = get_db()
    threads = db.execute("""
        SELECT * FROM threads;
    """).fetchall()

    return render_template("index.html", threads=threads)

@app.route("/<int:thread_id>")
def thread(thread_id):
    db = get_db()
    thread = db.execute("""
        SELECT * FROM threads
        WHERE thread_id = ?;
    """, (thread_id,)).fetchone()

    comments = db.execute("""
        SELECT * FROM comments
        WHERE thread_id = ?;
    """, (thread_id,)).fetchall()

    print(comments)

    return render_template("thread.html", thread=thread, comments=comments)

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
            """, (username, password))
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

        if user["password"] == password and username is not None:
            message = "Successful log in!"
            #return redirect("/")
        else:
            message = "Invalid username or password"

    return render_template("login.html", form=form, message=message)