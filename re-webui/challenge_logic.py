import json
import time
from os.path import join, dirname, realpath, isfile
from typing import Dict, Union, List

from .db import (
    get_db,
    close_db,
    fetch_solutions,
    fetch_user_by_id,
    fetch_functions_by_id,
    store_events,
    fetch_user_by_tmp_token,
    store_solution,
    store_notes,
    fetch_notes,
    store_new_function_name,
    fetch_events,
)

# -- Constants --
USER_ID_IDX = 0
FUNC_RENAME_OLD_IDX = 2
FUNC_RENAME_NEW_IDX = 3
NOTES_CONTENT_IDX = 3
EVENT_JSON_IDX = 0

MIN_SOLVES_REQUIRED = 0

# -- Utility Functions --


def get_timestamp() -> int:
    """Returns current timestamp in milliseconds."""
    return int(round(time.time() * 1000))


def get_json_file_path(filename: str, subpath: str) -> str:
    """Constructs the absolute path for a JSON data file."""
    base_dir = dirname(realpath(__file__))
    return join(base_dir, subpath, filename)


def load_json_data(filepath: str) -> Union[Dict, List, None]:
    """Safely loads JSON data from a file."""
    if not isfile(filepath):
        return None
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return None


def get_solved_count(db, user_id: int, _experiment_mode: int) -> int:
    """Returns the number of challenges solved by the user."""
    solves_cursor = fetch_solutions(db, (user_id,))

    return len(list(solves_cursor))


def build_function_map(
    db, user_id: int, challenge_num: int, json_path: str
) -> Dict[str, str]:
    """
    Builds a dictionary mapping original function names to their current (renamed) names.
    Structure: { 'original_name': 'current_name' }
    """
    # 1. Initialize map from functions.json (Base names)
    func_file_path = get_json_file_path("functions.json", json_path)
    function_map = {}

    if isfile(func_file_path):
        with open(func_file_path, "r") as f:
            for line in f:
                # Assuming one function name per line in functions.json
                original_name = line.strip()
                if original_name:
                    function_map[original_name] = original_name

    # 2. Apply Renames from Database
    renames = fetch_functions_by_id(db, (user_id, challenge_num))

    for record in sorted(renames):
        old_name = record[FUNC_RENAME_OLD_IDX]
        new_name = record[FUNC_RENAME_NEW_IDX]

        # If we have this old_name as a key (original name), update it
        if old_name in function_map:
            function_map[old_name] = new_name

        # If we have this old_name as a value (it was already renamed),
        # find the original key and update the value to the new name
        for original_key, current_val in function_map.items():
            if current_val == old_name:
                function_map[original_key] = new_name
                break

    return function_map


def log_event(
    db,
    user_id: int,
    challenge_num: int,
    function_name: str,
    event_type: str = "function_visit",
):
    """Logs a generic event to the database."""
    timestamp = get_timestamp()
    event_json = json.dumps(
        {
            "timestamp": timestamp,
            "event": event_type,
            "element": "",
            "fcn_name": function_name,
        }
    )
    store_events(db, (user_id, challenge_num, function_name, event_json))


# -- Template Logic Handlers --


def index_template(
    session, challenge_num, experiment_mode, obfuscation, request, json_path, g
):
    db = get_db()
    try:
        user_id = session.get("user_id")
        users = fetch_user_by_id(db, (user_id,))
        if not users:
            return False
        g.user = users[0]

        # Set Session Data
        session[f"obfuscation_{challenge_num}"] = obfuscation
        session["challenge_num"] = challenge_num
        session["addr"] = request.args.get("addr", "0")

        # Build Function Map
        function_map = build_function_map(db, user_id, challenge_num, json_path)

        # Determine Function Name to display/log
        req_func_name = request.args.get("function")
        final_func_name = req_func_name

        for original, current in function_map.items():
            if current == req_func_name:
                final_func_name = original
                break

        # Log and Finalize
        log_event(db, user_id, challenge_num, final_func_name)

        session["functions"] = function_map
        session["function_name"] = final_func_name
        return True
    finally:
        close_db()


def _generic_data_template(
    session, json_path, g, experiment_mode, challenge_num, data_filename, session_key
):
    """Generic handler for strings, callgraph, info pages."""
    db = get_db()
    try:
        user_id = session.get("user_id")

        # Check permissions
        solved_count = get_solved_count(db, user_id, experiment_mode)
        if solved_count < MIN_SOLVES_REQUIRED:
            return False

        # Load Data
        function_map = build_function_map(db, user_id, challenge_num, json_path)
        data_path = get_json_file_path(data_filename, json_path)
        data_content = load_json_data(data_path)

        # Set Context
        g.user = fetch_user_by_id(db, (user_id,))[0]
        session["functions"] = function_map
        if data_content and session_key:
            session[session_key] = data_content

        return True
    finally:
        close_db()


def strings_template(session, json_path, g, experiment_mode, challenge_num):
    return _generic_data_template(
        session, json_path, g, experiment_mode, challenge_num, "strings.json", "strings"
    )


def callgraph_template(session, json_path, g, experiment_mode, challenge_num):
    return _generic_data_template(
        session, json_path, g, experiment_mode, challenge_num, "functions.json", None
    )


def info_template(session, json_path, g, experiment_mode, challenge_num):
    return _generic_data_template(
        session, json_path, g, experiment_mode, challenge_num, "info.json", "info"
    )


def confirm_solution_template(session, experiment_mode):
    db = get_db()
    try:
        solved = get_solved_count(db, session["user_id"], experiment_mode)
        return solved >= MIN_SOLVES_REQUIRED
    finally:
        close_db()


def check_solution_template(request, session, challenge_num, correct_solution):
    db = get_db()
    try:
        user_solution = request.form.get("solution")
        if user_solution == correct_solution:
            store_solution(db, (session.get("user_id"), challenge_num, user_solution))
            if "status_solutions" in session:
                session["status_solutions"][challenge_num] = 1
            return True
        return False
    finally:
        close_db()


def get_call_graph_template(request, json_path):
    if request.method == "POST":
        func_required = request.form.get("name")
        if func_required == "callgraph":
            path = get_json_file_path(f"{func_required}.json", json_path)
            if isfile(path):
                with open(path, "r") as f:
                    return f.read()
    return ""


def store_notes_template(request, challenge_num):
    if request.method == "POST":
        db = get_db()
        try:
            token = request.form.get("token")
            notes = request.form.get("notes")

            users = fetch_user_by_tmp_token(db, (token,))
            if not users:
                return False

            user = users[0]
            store_notes(db, (user[USER_ID_IDX], challenge_num, notes))
            return True
        finally:
            close_db()
    return False


def download_notes_template(request, challenge_num):
    if request.method == "POST":
        db = get_db()
        try:
            token = request.form.get("token")
            users = fetch_user_by_tmp_token(db, (token,))
            if not users:
                return False

            user = users[0]
            note_record = fetch_notes(db, (user[USER_ID_IDX], challenge_num))
            if len(note_record):
                return note_record[0][NOTES_CONTENT_IDX]
            return ""  # Or None
        finally:
            close_db()
    return False


def get_CFG_template(request, json_path, challenge_num):
    if request.method != "POST":
        return ""

    db = get_db()
    try:
        token = request.form.get("token")
        users = fetch_user_by_tmp_token(db, (token,))
        if not users:
            return False
        user = users[0]

        func_required = request.form.get("name")
        cfg_filename = f"{func_required}.json"
        cfg_path = get_json_file_path(cfg_filename, json_path)

        if not isfile(cfg_path):
            return ""

        # Load CFG
        with open(cfg_path, "r") as f:
            cfg_data = json.load(f)

        # Load Strings for Xref injection
        strings_path = get_json_file_path("strings.json", json_path)
        strings_data = load_json_data(strings_path)

        # Inject OpCodes from strings into CFG assembly
        # (Preserving original logic)
        if strings_data:
            for key, val in strings_data.items():
                if val[0]["xref"][0] == func_required:
                    # Logic to patch disassembly string
                    bbs_key = f"{func_required}_bbs"
                    if bbs_key in cfg_data:
                        disasm_str = json.dumps(cfg_data[bbs_key])
                        local_addr = val[2]["addr"][0]
                        opcode = val[3]["opcode"][0]

                        # Find address in string
                        search_str = f"{local_addr}:"
                        start_idx = disasm_str.find(search_str)
                        if start_idx != -1:
                            # Find end of instruction line (assumed \\ is newline escape in json dump)
                            end_idx = start_idx
                            while (
                                end_idx < len(disasm_str)
                                and disasm_str[end_idx] != "\\"
                            ):
                                end_idx += 1

                            # Reconstruct string
                            new_disasm = (
                                disasm_str[:start_idx]
                                + f"{local_addr}: {opcode}"
                                + disasm_str[end_idx:]
                            )
                            cfg_data[bbs_key] = json.loads(new_disasm)

        # Apply Function Renaming to CFG content
        function_map = build_function_map(
            db, user[USER_ID_IDX], challenge_num, json_path
        )

        # Serialize to string to perform replacements
        cfg_json_str = json.dumps(cfg_data)

        for original, current in function_map.items():
            if original != current:
                cfg_json_str = cfg_json_str.replace(original, current)

        return cfg_json_str

    finally:
        close_db()


def get_xrefs_from_template(request, json_path, challenge_num):
    return _handle_xref_request(
        request, json_path, challenge_num, "xrefs_from.json", is_from=True
    )


def get_xrefs_to_template(request, json_path, challenge_num):
    return _handle_xref_request(
        request, json_path, challenge_num, "xrefs_to.json", is_from=False
    )


def _handle_xref_request(request, json_path, challenge_num, filename, is_from):
    if request.method != "POST":
        return ""

    db = get_db()
    try:
        # Auth Check
        token = request.form.get("token")
        users = fetch_user_by_tmp_token(db, (token,))
        if not users:
            return "Unauthenticated data"
        user = users[0]

        func_required = request.form.get("name")

        # Load Xref Data
        xref_data = load_json_data(get_json_file_path(filename, json_path))
        if not xref_data or func_required not in xref_data:
            return ""

        # Helper to apply renames
        function_map = build_function_map(
            db, user[USER_ID_IDX], challenge_num, json_path
        )

        result_map = {}
        target_list = xref_data[func_required]

        if is_from:
            # Structure: "funcName@Address"
            for item in target_list:
                parts = item.split("@")
                if len(parts) < 2:
                    continue

                func_name, addr = parts[0], parts[1]
                key_str = f"{func_name}&&addr={addr}"

                # Check if this function has a rename
                display_name = function_map.get(func_name, func_name)

                # If renamed, key uses original name + addr, value is new name
                # If not renamed, key is same, value is original name
                result_map[key_str] = display_name
        else:
            # Structure: "funcName" (simple list of callers)
            for func_name in target_list:
                display_name = function_map.get(func_name, func_name)
                result_map[func_name] = display_name

        return json.dumps(result_map)

    finally:
        close_db()


def get_js_data_template(jsdata, challenge_num):
    try:
        parts = jsdata.split(";")
        if len(parts) != 2:
            return "Wrong request"

        token, json_payload = parts[0], parts[1]

        db = get_db()
        try:
            users = fetch_user_by_tmp_token(db, (token,))
            if not users:
                return "Unauthenticated data"
            user = users[0]

            data = json.loads(json_payload)

            # Handle specifics
            if data.get("event") == "func_rename":
                # element = original_name, value = new_name
                store_new_function_name(
                    db,
                    (user[USER_ID_IDX], data["element"], data["value"], challenge_num),
                )

            # Log event
            store_events(
                db,
                (
                    user[USER_ID_IDX],
                    challenge_num,
                    data.get("fcn_name", ""),
                    json_payload,
                ),
            )
            return "Ok"

        finally:
            close_db()
    except Exception:
        return "Error processing data"


def get_events_from_db_template(request, challenge_num):
    token = request.args.get("id")
    fcn_name = request.args.get("fcn_name")

    db = get_db()
    try:
        users = fetch_user_by_tmp_token(db, (token,))
        if not users:
            return False
        user = users[0]

        events = fetch_events(db, (user[USER_ID_IDX], challenge_num, fcn_name))

        response = []
        valid_types = {"comment", "rename", "func_rename"}

        for e in events:
            try:
                # e[0] is the json string
                d = json.loads(e[EVENT_JSON_IDX])
                if d.get("event") in valid_types:
                    response.append(d)
            except json.JSONDecodeError:
                continue

        return json.dumps(response)
    finally:
        close_db()


def load_logged_in_user_template(session, g):
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        db = get_db()
        try:
            users = fetch_user_by_id(db, (user_id,))
            g.user = users[0] if users else None
        finally:
            close_db()
