
from pathlib import Path

from Nexa import Blueprint, render_template
from Nexa.nserver import Response

from config.security import is_valid_session

main = Blueprint("main")
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _protected_template(template_name):
    if not is_valid_session():
        return Response("", status=302, headers={"Location": "/login"})
    return render_template(template_name)


@main.route("/get-started")
def get_started():
    return render_template("get-started.html")


@main.route("/describe-yourself")
def describe_yourself():
    return _protected_template("describe-yourself.html")


@main.route("/login")
def login_page():
    return render_template("login.html")


@main.route("/dashboard")
def dashboard():
    return _protected_template("dashboard.nxs")


@main.route("/settings")
def settings():
    return _protected_template("settings.html")


@main.route("/explore")
def explore():
    return render_template("career-explorer.html")


@main.route("/career-quiz")
def career_quiz():
    return render_template("career-quiz.html")


@main.route("/compare")
def compare():
    return render_template("career-compare.html")


@main.route("/career")
def career_detail():
    return render_template("career-roadmap.html")


@main.route("/my-learning")
def my_learning():
    return _protected_template("my-learning.html")


@main.get("/assets/<asset_name>")
def public_asset(asset_name):
    assets = {
        "careerpath.css": ("text/css; charset=utf-8", "static/careerpath.css"),
        "careerpath.js": ("text/javascript; charset=utf-8", "static/careerpath.js"),
        "career-explorer.js": ("text/javascript; charset=utf-8", "static/career-explorer.js"),
        "career-quiz.js": ("text/javascript; charset=utf-8", "static/career-quiz.js"),
        "career-compare.js": ("text/javascript; charset=utf-8", "static/career-compare.js"),
        "career-roadmap.js": ("text/javascript; charset=utf-8", "static/career-roadmap.js"),
        "my-learning.js": ("text/javascript; charset=utf-8", "static/my-learning.js"),
    }
    asset = assets.get(asset_name)
    if asset is None:
        return Response("Not found", status=404)
    content_type, relative_path = asset
    content = (PROJECT_ROOT / relative_path).read_bytes()
    return Response(
        content,
        content_type=content_type,
        headers={"Cache-Control": "no-cache", "X-Content-Type-Options": "nosniff"},
    )