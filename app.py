from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

test_threads = {
    "1": {
        "title": "Hello there!",
        "date": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
        "desc": "This is a test thread!"
    },
    "2": {
        "title": "Yo!",
        "date": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
        "desc": "Whassssssssuuuuuuup!"
    },
}

@app.route("/")
def index():

    return render_template("index.html", threads=test_threads)

@app.route("/<thread_id>")
def thread(thread_id):
    thread = test_threads[thread_id]

    return render_template("thread.html", thread=thread)