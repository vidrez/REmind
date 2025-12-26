from flask import (
    Blueprint,
    g,
    render_template,
    request,
    session,
    redirect,
    url_for,
    flash,
)
from .config import get_chall_config
from .auth import login_required

# Importing from the logic module refactored previously
from .challenge_logic import (
    index_template,
    strings_template,
    confirm_solution_template,
    callgraph_template,
    get_call_graph_template,
    info_template,
    store_notes_template,
    download_notes_template,
    get_CFG_template,
    get_xrefs_from_template,
    get_xrefs_to_template,
    get_js_data_template,
    get_events_from_db_template,
    load_logged_in_user_template,
)

bp = Blueprint(
    "first_chall",
    __name__,
    url_prefix="/first_chall",
    template_folder="templates/template_first/",
)

# -- Configuration --
CHALL_ID = 1
CONFIG = get_chall_config(CHALL_ID)

CHALLENGE_NUM = CHALL_ID
OBFUSCATION = CONFIG["obfuscation"]
EXPERIMENT_MODE = int(CONFIG["experiment_mode"])
JSON_PATH = "jsons/first_json/"  # Relative path for the logic helper


# -- Helper for Access Control --
def handle_access_denied():
    """Redirects to index with an error message."""
    flash(
        "Access denied. You must complete the previous steps to access this resource.",
        "danger",
    )
    return redirect(url_for("rev_webui.index"))


# -- Routes --


@bp.route("/")
@login_required
def first_chall():
    success = index_template(
        session, CHALLENGE_NUM, EXPERIMENT_MODE, OBFUSCATION, request, JSON_PATH, g
    )
    if not success:
        return handle_access_denied()

    return render_template("first_chall.html")


@bp.route("/strings")
@login_required
def strings():
    success = strings_template(session, JSON_PATH, g, EXPERIMENT_MODE, CHALLENGE_NUM)
    if not success:
        return handle_access_denied()

    return render_template("strings.html")


@bp.route("/confirm_solution", methods=("GET", "POST"))
@login_required
def confirm_solution():
    success = confirm_solution_template(session, EXPERIMENT_MODE)
    if not success:
        return handle_access_denied()

    return render_template("confirm_solution.html")


@bp.route("/callgraph")
@login_required
def callgraph():
    success = callgraph_template(session, JSON_PATH, g, EXPERIMENT_MODE, CHALLENGE_NUM)
    if not success:
        return handle_access_denied()

    return render_template("callgraph.html")


@bp.route("/info")
@login_required
def info():
    success = info_template(session, JSON_PATH, g, EXPERIMENT_MODE, CHALLENGE_NUM)
    if not success:
        return handle_access_denied()

    return render_template("info.html")


# -- API Endpoints --


@bp.route("/getCallGraph", methods=["POST"])
def getCallGraph():
    return get_call_graph_template(request, JSON_PATH)


@bp.route("/storeNotes", methods=["POST"])
def storeNotes():
    success = store_notes_template(request, CHALLENGE_NUM)
    return "ok" if success else ("Unauthenticated data", 403)


@bp.route("/downloadNotes", methods=["POST"])
def downloadNotes():
    note = download_notes_template(request, CHALLENGE_NUM)
    return note if note is not False else ("Unauthenticated data", 403)


@bp.route("/getCFG", methods=["POST"])
def getCFG():
    result = get_CFG_template(request, JSON_PATH, CHALLENGE_NUM)
    return result if result else ("Unauthenticated data", 403)


@bp.route("/get_xrefs_from", methods=["POST"])
def get_xrefs_from():
    result = get_xrefs_from_template(request, JSON_PATH, CHALLENGE_NUM)
    return result if result else ("Unauthenticated data", 403)


@bp.route("/get_xrefs_to", methods=["POST"])
def get_xrefs_to():
    result = get_xrefs_to_template(request, JSON_PATH, CHALLENGE_NUM)
    return result if result else ("Unauthenticated data", 403)


@bp.route("/getmethod/<jsdata>")
def get_js_data(jsdata):
    return get_js_data_template(jsdata, CHALLENGE_NUM)


@bp.route("/getevents/")
def get_events_from_db():
    result = get_events_from_db_template(request, CHALLENGE_NUM)
    return result if result else ("Unauthenticated data", 403)


@bp.before_request
def load_logged_in_user():
    load_logged_in_user_template(session, g)
