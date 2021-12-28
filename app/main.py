import hashlib
import json
import os
from time import time
from typing import Dict, Optional, Union

from flask import Flask, render_template, request
from flask.typing import ResponseReturnValue

APP_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(APP_DIR, "static")
DATA_DIR = os.path.join(APP_DIR, "data")

HASHING_ALGORITHM = hashlib.sha3_512

app = Flask(__name__, static_folder=STATIC_DIR)


@app.errorhandler(404)
def page_not_found(e=None) -> ResponseReturnValue:
    return "Invalid address!", 404


@app.errorhandler(403)
def unauthorized(e=None) -> ResponseReturnValue:
    return "Unauthorized!", 403


@app.route("/")
def index() -> ResponseReturnValue:
    return render_template("index.html")


def _fresh_note(name: str) -> ResponseReturnValue:
    context = {"name": name, "authorized": True}
    return render_template("notes.html", context=context)


@app.route("/<name>", methods=["GET"])
def get_note(name):
    context = {"name": name}
    note_path = os.path.join(DATA_DIR, f"{name}.json")
    note_existed = os.path.isfile(note_path)
    if not note_existed:
        return _fresh_note(name)
    with open(note_path, "r") as inf:
        data = json.loads(inf.read())
    if (ttl := data.get("ttl")) and ttl < time():
        os.remove(note_path)
        return _fresh_note(name)
    if data.get("password"):
        context["message"] = "Note is password-protected"
        return render_template("notes.html", context=context)
    context["authorized"] = True
    context["content"] = data["content"]
    context["ttl"] = int(data["ttl"] - time()) if data["ttl"] is not None else ""
    return render_template("notes.html", context=context)


@app.route("/<name>", methods=["POST"])
def post_note(name) -> ResponseReturnValue:
    context = {"name": name}
    note_path = os.path.join(DATA_DIR, f"{name}.json")
    note_existed = os.path.isfile(note_path)
    content = request.form.get("content")
    get_ttl = request.form.get("ttl", "")
    try:
        ttl = int(get_ttl)
    except ValueError:
        ttl = None
    else:
        if ttl <= 0:
            return _fresh_note(name)
    ttl_timestamp = ttl + time() if ttl is not None else None
    password = ""
    if (request_password := request.form.get("password")):
        password = HASHING_ALGORITHM(request_password.encode()).hexdigest()
    if not note_existed:
        return _post_new_note(content, context, note_path, password, ttl_timestamp)
    return _post_existing_note(content, context, note_path, password, ttl_timestamp)


def _post_existing_note(
    content: Optional[str],
    context: Dict[str, Union[str, bool, None]],
    note_path: str,
    password: str,
    ttl: Optional[int],
) -> ResponseReturnValue:
    with open(note_path, "r") as inf:
        data = json.loads(inf.read())
    if (data_ttl := data["ttl"]) is not None and data_ttl < time():
        os.remove(note_path)
        return _fresh_note(context["name"])
    if (previous_password := data["password"]) and (previous_password != password):
        return unauthorized()
    context["authorized"] = True
    if content is None:
        context["content"] = data["content"]
        return render_template("notes.html", context=context)
    data = {"content": content, "password": password, "ttl": ttl}
    with open(note_path, "w") as ouf:
        ouf.write(json.dumps(data))
    context["message"] = "Note saved"
    context["content"] = content
    context["ttl"] = context["ttl"] = int(ttl - time()) if ttl is not None else ""
    return render_template("notes.html", context=context)


def _post_new_note(
    content: Optional[str],
    context: Dict[str, Union[str, bool, None]],
    note_path: str,
    password: str,
    ttl: Optional[int],
) -> ResponseReturnValue:
    data = {"content": content, "password": password, "ttl": ttl}
    with open(note_path, "w") as ouf:
        ouf.write(json.dumps(data))
    context["message"] = "Note saved"
    context["authorized"] = True
    context["content"] = content
    context["ttl"] = int(ttl - time()) if ttl is not None else ""
    return render_template("notes.html", context=context)


if __name__ == "__main__":
    # Only for debugging while developing
    app.run(host="0.0.0.0", debug=True, port=8001)
