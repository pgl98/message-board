from crypt import methods
from datetime import datetime, timedelta

from flask import Blueprint, request, current_app, abort, make_response, jsonify, Response
from functools import wraps
import json
import jwt
from werkzeug.security import generate_password_hash, check_password_hash

from database import get_db_api

api_bp = Blueprint('api', __name__)

# error handlers
@api_bp.errorhandler(401)
def custom_401(error):
    return Response('Invalid Credentials', 401, {'WWW-Authenticate':'Basic realm="Login Required"'})

@api_bp.errorhandler(404)
def custom_404(error):
    return Response('Resource not found.', 404)

# when a user has a token and makes a request, it should be placed at the 'Authorization' header
def api_login_required(view):
    @wraps(view)
    def decorated_function(**kwargs):
        try:
            jwt.decode(request.headers["Authorization"], key=current_app.config["SECRET_KEY"], algorithms='HS256')
        except:
            abort(401)

        return view(**kwargs)
    return decorated_function


@api_bp.route("/threads")
def threads():
    db = get_db_api()

    threads = db.execute("""
        SELECT * FROM threads;
    """).fetchall()

    return json.dumps(threads)

# returns a dict with "thread" and "comments" as keys
@api_bp.route("/threads/<int:thread_id>")
def thread(thread_id):
    db = get_db_api()

    thread = db.execute("""
        SELECT * FROM threads
        WHERE thread_id = ?;
    """, (thread_id,)).fetchone()

    comments = db.execute("""
        SELECT * FROM comments
        WHERE thread_id = ?;
    """, (thread_id,)).fetchall()

    if thread is None:
        abort(404)

    response = {
        "thread": thread,
        "comments": comments
    }


    return json.dumps(response)


@api_bp.route("/create_thread", methods=["POST"])
@api_login_required
def create_thread():
    username = jwt.decode(request.headers["Authorization"], key=current_app.config["SECRET_KEY"], algorithms='HS256')["sub"]
    data = request.get_json()
    title = data["title"]
    body = data["body"]
    date_created = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

    db = get_db_api()
    db.execute("""
        INSERT INTO threads (title, body, date_created, user_poster)
        VALUES (?, ?, ?, ?);
    """, (title, body, date_created, username,))
    db.commit()

    return "", 201

@api_bp.route("/delete_thread/<int:thread_id>", methods=["POST"])
@api_login_required
def delete_thread(thread_id):
    token_data = jwt.decode(request.headers["Authorization"], key=current_app.config["SECRET_KEY"], algorithms='HS256')
    username = token_data["sub"]
    is_admin = token_data["is_admin"]

    db = get_db_api()
    thread = db.execute("""
        SELECT * FROM threads
        WHERE thread_id = ?;
    """, (thread_id,)).fetchone()

    if thread is None:
        abort(404)
    elif username == thread["user_poster"] or is_admin:
        db.execute("""
        DELETE FROM threads
        WHERE thread_id = ?;
        """, (thread_id,))

        db.execute("""
            DELETE FROM comments
            WHERE thread_id = ?;
        """, (thread_id,))

        db.commit()

        return "", 204
    else:
        abort(400)

# to make a comment on a thread, send a POST request with comment in json
@api_bp.route("/comment/<int:thread_id>", methods=["POST"])
@api_login_required
def comment(thread_id):
    username = jwt.decode(request.headers["Authorization"], key=current_app.config["SECRET_KEY"], algorithms='HS256')["sub"]
    body = request.get_json()["comment"]
    date_created = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")

    db = get_db_api()
    db.execute("""
        INSERT INTO comments (thread_id, username, date_created, body)
        VALUES (?, ?, ?, ?);
    """, (thread_id, username, date_created, body,))
    db.commit()

    return "", 201

@api_bp.route("/delete_comment/<int:comment_id>", methods=["POST"])
@api_login_required
def delete_comment(comment_id):
    token_data = jwt.decode(request.headers["Authorization"], key=current_app.config["SECRET_KEY"], algorithms='HS256')
    username = token_data["sub"]
    is_admin = token_data["is_admin"]

    db = get_db_api()
    comment = db.execute("""
        SELECT * FROM comments
        WHERE comment_id = ?;
    """, (comment_id,)).fetchone()

    if comment is None:
        abort(404)
    elif username == comment["username"] or is_admin:
        db.execute("""
            DELETE FROM comments
            WHERE comment_id = ?;
        """, (comment_id,))

        db.commit()

        return "", 204
    else:
        abort(400)

    return "delete comment"

@api_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    db = get_db_api()

    # if username is already registered, the try block will give an error
    # since username is the primary key of the users table
    try:
        date_created = date_created = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        db.execute("""
            INSERT INTO users (username, password_hash, is_admin, date_created)
            VALUES (?, ?, ?, ?);
        """, (username, generate_password_hash(password), False, date_created))
        db.commit()
        return "", 201
    except:
        return "Username already taken. Try another one.", 409

# when a user successfully logs in, their token is sent back via json
# username and is_admin is stored in payload of token
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

            response = make_response(token)

            return response
    except:
        abort(401)