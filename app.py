from flask import Flask, render_template, redirect
from forms import ThreadForm
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