from crypt import methods
from datetime import datetime, timedelta

from flask import Blueprint, request, current_app, abort, make_response, jsonify
from functools import wraps
import json
import jwt
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db_api

api_bp = Blueprint('api', __name__)


def api_login_required(view):
    @wraps(view)
    def decorated_function(**kwargs):
        token = request.headers["Authorization"]

        print(token)
        return view(**kwargs)
    return decorated_function


@api_bp.route("/threads")
def threads():
    db = get_db_api()

    threads = db.execute("""
        SELECT * FROM threads;
    """).fetchall()

    return json.dumps(threads)

@api_bp.route("/threads/<int:thread_id>")
def thread(thread_id):
    db = get_db_api()

    thread = db.execute("""
        SELECT * FROM threads
        WHERE thread_id = ?;
    """, (thread_id,)).fetchone()

    return json.dumps(thread)

@api_bp.route("/comment/<int:thread_id>", methods=["POST"])
@api_login_required
def comment(thread_id):
    data = jwt.decode(request.headers["Authorization"], key=current_app.config["SECRET_KEY"], algorithms='HS256')

    print(data)

    db = get_db_api()

    thread = db.execute("""
        SELECT * FROM threads
        WHERE thread_id = ?;
    """, (thread_id,)).fetchone()

    return "comment"


@api_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    db = get_db_api()

    try:
        user = db.execute("""
            SELECT * FROM users
            WHERE username = ?;
            """, (username,)).fetchone()

        password_is_valid = check_password_hash(user["password_hash"], password)

        if user is not None and password_is_valid:
            payload = {
                "sub": username,
                "iat": datetime.now(),
                "exp": datetime.now() + timedelta(minutes=30),
                "is_admin": user["is_admin"]
            }

            token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm='HS256')

            response = make_response(jsonify({"Authorization": token}))

            return response
    except:
        abort(401)