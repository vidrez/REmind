import mysql.connector
from flask import current_app, g


def get_db():
    """Connect to the database and store connection in g for the request duration."""

    if "db" not in g:
        try:
            g.db = mysql.connector.connect(
                host=current_app.config["MYSQL_HOST"],
                user=current_app.config["MYSQL_USER"],
                password=current_app.config["MYSQL_PASSWORD"],
                database=current_app.config["MYSQL_DATABASE"],
            )
        except mysql.connector.Error as e:
            raise Exception(e)
            return None

    return g.db


def close_db(e=None):
    """Close the database connection at the end of the request."""
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_app(app):
    """Register database functions with the Flask app."""
    app.teardown_appcontext(close_db)


def read_query(db, query, params=None):
    """
    Executes a SELECT query safely using parameterized queries.
    """
    cursor = db.cursor()
    try:
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        cursor.close()


def write_query(db, query, params):
    """
    Executes INSERT/UPDATE queries safely using parameterized queries.
    """
    cursor = db.cursor()
    try:
        cursor.execute(query, params)
        db.commit()
    finally:
        cursor.close()


def register_user(db, params):
    q = "INSERT INTO user (lev, token, tmp_token, solves, first_name, last_name, other) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    write_query(db, q, params)


def store_solution(db, params):
    q = "INSERT INTO solutions (user_id, challenge, solution) values(%s, %s, %s)"
    write_query(db, q, params)


def fetch_solutions(db, params):
    q = "SELECT * FROM solutions WHERE user_id = %s GROUP BY challenge"
    return read_query(db, q, params)


def fetch_user_by_token(db, params):
    q = "SELECT * FROM user WHERE token = %s"
    return read_query(db, q, params)


def update_tmp_token(db, params):
    q = "UPDATE user SET tmp_token = %s WHERE id = %s"
    write_query(db, q, params)


def fetch_user_by_id(db, params):
    q = "SELECT * FROM user WHERE id = %s"
    return read_query(db, q, params)


def fetch_user_by_tmp_token(db, params):
    q = "SELECT * FROM user WHERE tmp_token = %s"
    return read_query(db, q, params)


def store_new_function_name(db, params):
    q = "INSERT INTO func (user_id, old_name, new_name, challenge) VALUES (%s, %s, %s, %s)"
    write_query(db, q, params)


def fetch_functions_by_id(db, params):
    q = "SELECT * FROM func WHERE user_id = %s AND challenge = %s"
    return read_query(db, q, params)


def store_notes(db, params):
    q = "INSERT INTO notes (user_id, challenge, note) VALUES (%s, %s, %s)"
    write_query(db, q, params)


def fetch_notes(db, params):
    q = "SELECT * FROM notes WHERE user_id = %s AND challenge = %s ORDER BY id DESC LIMIT 1"
    return read_query(db, q, params)


def store_events(db, params):
    q = "INSERT INTO events (user_id, challenge, fcn_name, event) VALUES (%s, %s, %s, %s)"
    write_query(db, q, params)


def fetch_events(db, params):
    q = "SELECT event FROM events WHERE user_id = %s AND challenge = %s AND fcn_name = %s"
    return read_query(db, q, params)
