from datetime import datetime

from flask import render_template, redirect, request, url_for, Blueprint, session
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db
from forms import LoginForm, RegisterForm

auth_bp = Blueprint('auth', __name__, template_folder='../auth/templates/auth')

@auth_bp.route("/register", methods=["GET", "POST"])
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
            date_created = date_created = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
            db.execute("""
                INSERT INTO users (username, password_hash, is_admin, date_created)
                VALUES (?, ?, ?, ?);
            """, (username, generate_password_hash(password), False, date_created))
            db.commit()
            return redirect( url_for("auth.login", message="Successful Registration") )
        except Exception as e:
            # For now, force user to put in password again. May change later.
            # let them see the taken username, though.
            form.password.data = None
            message = "Username already taken. Try another one."

    return render_template("register.html", form=form, message=message)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    username = None
    password = None
    message = request.args.get("message")

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
                session["is_admin"] = user["is_admin"]

                # look at 'login_required' decorator
                next_page = request.args.get("next")
                if not next_page:
                    next_page = url_for("thread.index")
                return redirect(next_page)
            else:
                message = "Invalid username or password"
                return redirect( url_for('login', message=message))
        except:
            # don't specify which of the username or password is wrong for better security
            message = "Invalid username or password"
    else:
        message = ""

    return render_template("login.html", form=form, message=message)

@auth_bp.route("/logout")
def logout():
    session.clear()

    return redirect( url_for("auth.login") )