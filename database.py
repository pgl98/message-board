import os
import sqlite3

from flask import g 

DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), "app.db")

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_db_api():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = dict_factory
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()