from flask import (
    Blueprint,
    g,
    render_template,
    request,
    session,
    redirect,
    url_for,
    flash,
    jsonify,
)
from .config import get_chall_config
from .auth import login_required

# Importing from the refactored logic module
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
    "challenge",
    __name__,
    url_prefix="/challenge",
    template_folder="templates/challenge_view/",  # Shared folder for all challenges
)

# -- Modular Context Helper --


def get_chall_ctx(chall_id):
    """
    Fetches configuration and calculates paths dynamically based on ID.
    Replaces the hardcoded constants found in previous versions.
    """
    config = get_chall_config(chall_id)
    if not config:
        return None

    return {
        "id": chall_id,
        "obfuscation": config.get("obfuscation", "True") == "True",
        "experiment_mode": int(config.get("experiment_mode", 0)),
        "json_path": f"jsons/chall_{chall_id}_json/",  # Standardized folder pattern
    }


def handle_access_denied():
    """Redirects to dashboard with a standardized error message."""
    flash(
        "Access denied. You must complete the previous steps to access this resource.",
        "danger",
    )
    return redirect(url_for("rev_webui.index"))


# -- Dynamic Routes --


@bp.route("/<int:chall_id>/")
@login_required
def view(chall_id):
    ctx = get_chall_ctx(chall_id)
    if not ctx:
        return redirect(url_for("rev_webui.index"))

    success = index_template(
        session,
        ctx["id"],
        ctx["experiment_mode"],
        ctx["obfuscation"],
        request,
        ctx["json_path"],
        g,
    )
    if not success:
        return handle_access_denied()

    # Always render the same shared template
    return render_template("view.html", chall_id=chall_id)


@bp.route("/<int:chall_id>/strings")
@login_required
def strings(chall_id):
    ctx = get_chall_ctx(chall_id)
    if not ctx:
        return handle_access_denied()

    success = strings_template(
        session, ctx["json_path"], g, ctx["experiment_mode"], ctx["id"]
    )
    if not success:
        return handle_access_denied()

    return render_template("strings.html", chall_id=chall_id)


@bp.route("/<int:chall_id>/confirm_solution", methods=("GET", "POST"))
@login_required
def confirm_solution(chall_id):
    ctx = get_chall_ctx(chall_id)
    if not ctx:
        return handle_access_denied()

    success = confirm_solution_template(session, ctx["experiment_mode"])
    if not success:
        return handle_access_denied()

    return render_template("confirm_solution.html", chall_id=chall_id)


@bp.route("/<int:chall_id>/callgraph")
@login_required
def callgraph(chall_id):
    ctx = get_chall_ctx(chall_id)
    if not ctx:
        return handle_access_denied()

    success = callgraph_template(
        session, ctx["json_path"], g, ctx["experiment_mode"], ctx["id"]
    )
    if not success:
        return handle_access_denied()

    return render_template("callgraph.html", chall_id=chall_id)


@bp.route("/<int:chall_id>/info")
@login_required
def info(chall_id):
    ctx = get_chall_ctx(chall_id)
    if not ctx:
        return handle_access_denied()

    success = info_template(
        session, ctx["json_path"], g, ctx["experiment_mode"], ctx["id"]
    )
    if not success:
        return handle_access_denied()

    return render_template("info.html", chall_id=chall_id)


# -- API Endpoints (All use ctx for dynamic pathing) --


@bp.route("/<int:chall_id>/getCallGraph", methods=["POST"])
def getCallGraph(chall_id):
    ctx = get_chall_ctx(chall_id)
    if not ctx:
        return "", 404
    return get_call_graph_template(request, ctx["json_path"])


@bp.route("/<int:chall_id>/storeNotes", methods=["POST"])
def storeNotes(chall_id):
    success = store_notes_template(request, chall_id)
    return "ok" if success else ("Unauthenticated data", 403)


@bp.route("/<int:chall_id>/downloadNotes", methods=["POST"])
def downloadNotes(chall_id):
    note = download_notes_template(request, chall_id)
    return note if note is not False else ("Unauthenticated data", 403)


@bp.route("/<int:chall_id>/getCFG", methods=["POST"])
def getCFG(chall_id):
    ctx = get_chall_ctx(chall_id)
    if not ctx:
        return jsonify({"error": "not found"}), 404
    result = get_CFG_template(request, ctx["json_path"], chall_id)
    return (
        (result, 200, {"Content-Type": "application/json"})
        if result
        else (jsonify({"error": "denied"}), 403)
    )


@bp.route("/<int:chall_id>/get_xrefs_from", methods=["POST"])
def get_xrefs_from(chall_id):
    ctx = get_chall_ctx(chall_id)
    if not ctx:
        return jsonify({"error": "not found"}), 404
    result = get_xrefs_from_template(request, ctx["json_path"], chall_id)
    return (
        (result, 200, {"Content-Type": "application/json"})
        if result
        else (jsonify({"error": "denied"}), 403)
    )


@bp.route("/<int:chall_id>/get_xrefs_to", methods=["POST"])
def get_xrefs_to(chall_id):
    ctx = get_chall_ctx(chall_id)
    if not ctx:
        return jsonify({"error": "not found"}), 404
    result = get_xrefs_to_template(request, ctx["json_path"], chall_id)
    return (
        (result, 200, {"Content-Type": "application/json"})
        if result
        else (jsonify({"error": "denied"}), 403)
    )


@bp.route("/<int:chall_id>/getmethod/<jsdata>")
def get_js_data(chall_id, jsdata):
    return get_js_data_template(jsdata, chall_id)


@bp.route("/<int:chall_id>/getevents/")
def get_events_from_db(chall_id):
    result = get_events_from_db_template(request, chall_id)
    return (
        (result, 200, {"Content-Type": "application/json"})
        if result
        else (jsonify({"error": "denied"}), 403)
    )


@bp.before_request
def load_logged_in_user():
    load_logged_in_user_template(session, g)
