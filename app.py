from flask import Flask, render_template, redirect
from forms import ThreadForm, RegisterForm, LoginForm
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "this-is-my-secret-key"

test_threads = {
    "1": {
        "title": "Hello there!",
        "date": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
        "body": "This is a test thread!"
    },
    "2": {
        "title": "Yo!",
        "date": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
        "body": "Whassssssssuuuuuuup!"
    },
}

test_users = {
    "admin": "admin",
    "derek": "bridge"
}

@app.route("/")
def index():

    return render_template("index.html", threads=test_threads)

@app.route("/<thread_id>")
def thread(thread_id):
    thread = test_threads[thread_id]

    return render_template("thread.html", thread=thread)

@app.route("/post_thread", methods=["GET", "POST"])
def post_thread():
    form = ThreadForm()

    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        date = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

        id = str(len(test_threads.keys()) + 1)
        test_threads[id] = {
            "title": title,
            "body": body,
            "date": date
        }

        return redirect("/")
    
    return render_template("thread_form.html", form=form)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    message = None

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        if username in test_users:
            message = "Username is already taken. Try another one."
        else:
            test_users[username] = password
            message = "Successful Registration"

            return redirect("login")

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

        try:
            if test_users[username] == password:
                return redirect("/")
        except:
            message = "Invalid username or password"

    return render_template("login.html", form=form, message=message)