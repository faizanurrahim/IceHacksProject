
from Nexa import Blueprint, jsonify
from config.careers import careers as _careers
from config.ERR import RaiseJSONErr
from config.career_catalog import find_career

career_by_id = {
    career_id: name
    for name, career_id in _careers.items()
}

api = Blueprint("api", "/api/v1")


@api.route("/health")
def api_index():
    return jsonify({"health": "good"})


api.route("/careers")(lambda: jsonify(_careers))


@api.get("/career/<id>")
def careerById(id):
    try:
        career_id = int(id)
    except ValueError:
        return RaiseJSONErr("Invalid career ID", 400)

    selected_career = career_by_id.get(career_id)

    if selected_career is None:
        return RaiseJSONErr("Career not found", 404)

    details = find_career(career_id)
    if details is None:
        return RaiseJSONErr("Career not found", 404)
    return jsonify(details)
