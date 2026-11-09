import logging

from Nexa import Blueprint
from Nexa.nserver import request

from config.ERR import RaiseJSONErr
from config.career_catalog import (
    CAREER_CATEGORIES,
    find_career,
    get_career_catalog,
    quiz_recommendations,
)
from config.careers import careers
from config.security import json_response

career_explorer_api = Blueprint("careerExplorerAPI", "/api/v1")
VALID_WORK_STYLES = {
    "people", "analytical", "hands_on", "creative", "structured", "independent",
}


def _positive_id(value):
    try:
        career_id = int(value)
    except (TypeError, ValueError):
        return None
    return career_id if career_id in set(careers.values()) else None


@career_explorer_api.get("/explore/careers")
def explore_careers():
    query = request.args.get("search", "")
    category = request.args.get("category", "")
    if not isinstance(query, str) or not isinstance(category, str):
        return RaiseJSONErr("Invalid search filters", 400)
    query = query.strip().casefold()[:100]
    category = category.strip()
    if category and category not in CAREER_CATEGORIES:
        return RaiseJSONErr("Unknown career category", 400)

    results = get_career_catalog()
    if category:
        results = [career for career in results if career["category"] == category]
    if query:
        results = [
            career for career in results
            if query in career["name"].casefold()
            or query in career["description"].casefold()
            or query in career["category"].casefold()
            or any(query in skill.casefold() for skill in career["required_skills"])
        ]
    return json_response({
        "success": True,
        "categories": list(CAREER_CATEGORIES),
        "careers": results,
    })


@career_explorer_api.get("/career/<id>/roadmap")
def career_roadmap(id):
    career_id = _positive_id(id)
    if career_id is None:
        return RaiseJSONErr("Career not found", 404)
    career = find_career(career_id)
    return json_response({"success": True, "career": career})


@career_explorer_api.post("/careers/compare")
def compare_careers():
    data = request.json
    if not isinstance(data, dict):
        return RaiseJSONErr("Invalid JSON request", 400)
    ids = data.get("career_ids")
    if (
        not isinstance(ids, list)
        or not 2 <= len(ids) <= 4
        or not all(isinstance(item, int) and not isinstance(item, bool) for item in ids)
        or len(set(ids)) != len(ids)
    ):
        return RaiseJSONErr("Select 2 to 4 different career IDs", 400)
    selected = [find_career(career_id) for career_id in ids]
    if any(career is None for career in selected):
        return RaiseJSONErr("One or more career IDs are invalid", 400)
    return json_response({"success": True, "careers": selected})


@career_explorer_api.post("/career-quiz")
def career_quiz():
    data = request.json
    if not isinstance(data, dict):
        return RaiseJSONErr("Invalid JSON request", 400)
    fields = ("education", "subjects", "interests", "skills", "work_styles")
    if set(data) != set(fields):
        return RaiseJSONErr("Provide education, subjects, interests, skills, and work_styles", 400)
    education = data.get("education")
    if not isinstance(education, str) or not education.strip() or len(education) > 80:
        return RaiseJSONErr("Choose a valid education level", 400)
    answers = {"education": education.strip()}
    for field in ("subjects", "interests", "skills", "work_styles"):
        values = data.get(field)
        if (
            not isinstance(values, list)
            or not 1 <= len(values) <= 12
            or not all(isinstance(value, str) and value.strip() and len(value) <= 80 for value in values)
        ):
            return RaiseJSONErr(f"Choose between 1 and 12 valid {field.replace('_', ' ')}", 400)
        answers[field] = list(dict.fromkeys(value.strip() for value in values))
    invalid_styles = set(answers["work_styles"]) - VALID_WORK_STYLES
    if invalid_styles:
        return RaiseJSONErr("One or more work styles are invalid", 400)
    try:
        return json_response({
            "success": True,
            "recommendations": quiz_recommendations(answers),
        })
    except (KeyError, TypeError, ValueError):
        logging.exception("Career quiz scoring error")
        return RaiseJSONErr("Unable to generate career recommendations", 500)
