import functools
import json
import os
import binascii
from typing import Dict
import sys
from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from .config import get_general_config
from .db import (
    get_db,
    register_user,
    fetch_solutions,
    update_tmp_token,
    fetch_user_by_id,
    fetch_user_by_token,
)


bp = Blueprint("auth", __name__, url_prefix="/auth", template_folder="templates/auth/")

CONFIG = get_general_config()
EXPERIMENT_MODE = CONFIG.get("experiment_mode", 0)

# Database User Tuple Indices
USER_ID_IDX = 0
USER_TOKEN_IDX = 2

# Config constant for challenges
NUM_CHALLENGES = 7


def _get_submitted_solutions(db, user_id: int) -> Dict[int, int]:
    """
    Retrieves the solution status for a given user.
    Returns a dictionary mapping challenge IDs to 1 (solved) or 0 (unsolved).
    """
    solutions_map = {i: 0 for i in range(1, NUM_CHALLENGES + 1)}
    solved_records = fetch_solutions(db, (user_id,))

    for record in solved_records:
        challenge_num = record[2]
        solutions_map[challenge_num] = 1

    return solutions_map


@bp.route("/token", methods=["POST"])
def token():
    """
    API Endpoint: Generates a new random token and registers a new user with it.
    Returns: JSON containing the new token.
    """
    db = get_db()

    new_token = binascii.hexlify(os.urandom(5)).decode("utf-8")
    hashed_token = new_token

    # Create user tuple structure: (ID, Token, ..., placeholders)
    new_user_data = (0, hashed_token, "", 0, "", "", "")
    register_user(db, new_user_data)

    # Automatically set the session token
    session["token"] = new_token

    return json.dumps({"token": new_token})


@bp.route("/token/validate", methods=["POST"])
def token_validity():
    """
    API Endpoint: Validates if a submitted token exists in the database.
    """
    db = get_db()
    data = request.get_json()

    if not data or "token" not in data:
        return json.dumps({"valid": False, "error": "Missing token"}), 400

    token_str = data["token"]
    user = fetch_user_by_token(db, (token_str,))

    if user:
        session["token"] = token_str
        return json.dumps({"valid": True})
    else:
        return json.dumps({"valid": False})


@bp.route("/login", methods=("GET", "POST"))
def login():
    """
    Handles user login via token.
    """
    if request.method == "POST":
        input_token = request.form["token"]
        db = get_db()
        error = None

        user = fetch_user_by_token(db, (input_token,))

        if not len(user):
            error = "Incorrect token"

        if error is None:
            user = user[0]
            session.clear()

            user_id = user[USER_ID_IDX]
            session["user_id"] = user_id
            session["status_solutions"] = _get_submitted_solutions(db, user_id)

            tmp_token = binascii.hexlify(os.urandom(10)).decode("utf-8")
            update_tmp_token(db, (tmp_token, user_id))
            session["tmp_token"] = tmp_token

            return redirect(url_for("rev_webui.index"))

        flash(error)

    return render_template("login.html")


@bp.route("/logout")
def logout():
    """
    Logs out the current user, clears the temp token in DB, and clears session.
    """
    user_id = session.get("user_id")

    if user_id:
        db = get_db()
        update_tmp_token(db, ("", user_id))

    session.clear()

    return redirect(url_for("rev_webui.index"))


@bp.before_app_request
def load_logged_in_user():
    """
    Runs before every request to load the current user into the global 'g' object.
    """
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = fetch_user_by_id(get_db(), (user_id,))


def login_required(view):
    """
    Decorator to ensure a user is logged in before accessing a view.
    Redirects to login page if no user is found in 'g'.
    """

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view
