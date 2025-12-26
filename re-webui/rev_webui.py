import json
import time
from flask import (
    Blueprint,
    g,
    render_template,
    request,
    session,
)

from .db import get_db, write_query, read_query
from .config import get_general_config
from .auth import login_required

# -- Configuration & Constants --
bp = Blueprint("rev_webui", __name__, template_folder="templates/general/")

CONFIG = get_general_config()
NUM_CHALLENGES = CONFIG["challs"]
EXPERIMENT_MODE = CONFIG["experiment_mode"]

# Index in the user tuple representing the 'solves' column
USER_SOLVES_COLUMN_INDEX = 4


def get_timestamp() -> int:
    """Returns current timestamp in milliseconds."""
    return int(round(time.time() * 1000))


def get_submitted_solutions_map(db, user_id: int) -> dict:
    """
    Returns a dictionary mapping challenge IDs to status (1 for solved, 0 for unsolved).
    """
    # Initialize all challenges as unsolved (0)
    solutions_map = {i: 0 for i in range(1, NUM_CHALLENGES)}

    query = "SELECT * FROM solutions WHERE user_id = %s GROUP BY challenge"
    solved_records = read_query(db, query, (user_id,))

    for record in solved_records:
        challenge_num = record[2]
        solutions_map[challenge_num] = 1

    return solutions_map


def _handle_solution_submission(db, user_id: int):
    """Processes the POST request for submitting a solution."""
    solution_text = request.form["solution"]

    payload = {"timestamp": get_timestamp(), "solution": solution_text}
    solution_json = json.dumps(payload)

    # Default to challenge 1 if not set in session
    challenge_num = session.get("challenge_num", 1)

    write_query(
        db,
        "INSERT INTO solutions (user_id, challenge, solution) VALUES (%s, %s, %s)",
        (user_id, challenge_num, solution_json),
    )


# -- Routes --


@bp.before_request
def load_logged_in_user():
    """
    Loads the user object into g.user before every request in this blueprint.
    """
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        user_data = read_query(get_db(), "SELECT * FROM user WHERE id = %s", (user_id,))
        g.user = user_data[0] if user_data else None


@bp.route("/", methods=("GET", "POST"))
@login_required
def index():
    db = get_db()
    user_id = session.get("user_id")

    if request.method == "POST":
        _handle_solution_submission(db, user_id)

    solved_records = read_query(
        db, "SELECT * FROM solutions WHERE user_id = %s GROUP BY challenge", (user_id,)
    )

    current_solves_count = len(solved_records)
    session["solves"] = current_solves_count
    session["status_solutions"] = get_submitted_solutions_map(db, user_id)

    return render_template("exercises.html")


@bp.route("/congrats")
@login_required
def congrats():
    return render_template("congrats.html")


@bp.route("/wrong")
@login_required
def wrong():
    return render_template("wrong.html")
