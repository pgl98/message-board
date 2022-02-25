from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

test_threads = {
    "1": {
        "title": "Hello there!",
        "date": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
    },
    "2": {
        "title": "Yo!",
        "date": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
    },
}

@app.route("/")
def index():
    threads = test_threads.values()

    return render_template("index.html", threads=threads)