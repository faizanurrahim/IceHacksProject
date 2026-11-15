import logging

from bson import ObjectId
from Nexa import Blueprint
from Nexa.nserver import request
from pymongo.errors import PyMongoError

from config.ERR import RaiseJSONErr
from config.career_catalog import (
    CAREER_CATEGORIES,
    find_career,
    get_career_catalog,
)
from config.db import career_feedback, career_learning, users
from config.careers import careers
from config.security import authenticate_request, json_response
from AI.dataset import validate_feedback, normalize_quiz_answers
from AI.engine import recommend
from AI.learner import save_feedback, withdraw_training_feedback

career_explorer_api = Blueprint("careerExplorerAPI", "/api/v1")


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
    try:
        answers = normalize_quiz_answers(data)
    except ValueError as exc:
        return RaiseJSONErr(str(exc), 400)
    try:
        user_id, _ = authenticate_request()
        learning = (
            career_learning.find_one({"user_id": user_id})
            if user_id else None
        )
        result = recommend(
            answers,
            preferences=(learning or {}).get("recommendation_preferences"),
        )
        return json_response({
            "success": True,
            **result,
        })
    except PyMongoError:
        logging.exception("Career quiz preference lookup failed")
        return RaiseJSONErr("Unable to load saved recommendation preferences", 500)
    except (KeyError, TypeError, ValueError):
        logging.exception("Career quiz scoring error")
        return RaiseJSONErr("Unable to generate career recommendations", 500)


@career_explorer_api.post("/career-quiz/feedback")
def submit_career_feedback():
    data = request.json
    if not isinstance(data, dict):
        return RaiseJSONErr("Invalid JSON request", 400)
    user_id, auth_error = authenticate_request()
    if auth_error:
        return auth_error
    try:
        feedback = validate_feedback(data)
    except ValueError as exc:
        return RaiseJSONErr(str(exc), 400)

    try:
        if users.find_one({"_id": ObjectId(user_id)}, {"_id": 1}) is None:
            return RaiseJSONErr("User account not found", 401)
        is_new = save_feedback(
            user_id,
            feedback,
            career_feedback,
            career_learning,
        )
        return json_response({
            "success": True,
            "duplicate": not is_new,
            "training_consent": feedback["training_consent"],
            "stored_for_training": bool(is_new and feedback["training_consent"]),
            "message": (
                "Thanks. Your personal preferences were updated for future recommendations."
                if is_new else "This feedback submission was already received."
            ),
        })
    except PyMongoError:
        logging.exception("Career recommendation feedback save failed")
        return RaiseJSONErr("Unable to save recommendation feedback", 500)


@career_explorer_api.delete("/career-quiz/feedback/training-consent")
def withdraw_career_training_consent():
    user_id, auth_error = authenticate_request()
    if auth_error:
        return auth_error
    try:
        deleted_count = withdraw_training_feedback(user_id, career_feedback)
        return json_response({
            "success": True,
            "deleted_feedback_records": deleted_count,
            "message": (
                "Your opted-in feedback records were removed from future training datasets. "
                "Already-promoted aggregate models are not automatically unlearned."
            ),
        })
    except PyMongoError:
        logging.exception("Career training-consent withdrawal failed")
        return RaiseJSONErr("Unable to withdraw training consent", 500)
