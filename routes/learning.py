import logging
from datetime import datetime, timezone

from bson import ObjectId
from pymongo.errors import PyMongoError
from Nexa import Blueprint
from Nexa.nserver import request

from config.ERR import RaiseJSONErr
from config.career_catalog import find_career
from config.careers import careers
from config.db import career_learning, users
from config.security import authenticate_request, json_response

learning_api = Blueprint("learningAPI", "/api/v1/learning")


def _account(data=None):
    user_id, error_response = authenticate_request(data)
    if error_response:
        return None, error_response
    try:
        if users.find_one({"_id": ObjectId(user_id)}, {"_id": 1}) is None:
            return None, RaiseJSONErr("User account not found", 404)
    except PyMongoError:
        logging.exception("Learning account lookup failed")
        return None, RaiseJSONErr("Database operation failed", 500)
    return user_id, None


def _body():
    data = request.json
    if not isinstance(data, dict):
        return None, RaiseJSONErr("Invalid JSON request", 400)
    return data, None


def _career_id(data):
    career_id = data.get("career_id")
    if isinstance(career_id, bool) or not isinstance(career_id, int) or career_id not in careers.values():
        return None
    return career_id


def _ensure_document(user_id):
    career_learning.update_one(
        {"user_id": user_id},
        {"$setOnInsert": {"user_id": user_id, "created_at": datetime.now(timezone.utc)}},
        upsert=True,
    )


def _get_state(user_id):
    state = career_learning.find_one({"user_id": user_id}) or {}
    return {
        "favorites": state.get("favorites", []),
        "saved_roadmaps": state.get("saved_roadmaps", []),
        "completed_skills": state.get("completed_skills", {}),
        "quiz_results": state.get("quiz_results", []),
    }


@learning_api.get("/")
def get_learning_state():
    user_id, error_response = _account()
    if error_response:
        return error_response
    try:
        return json_response({"success": True, **_get_state(user_id)})
    except PyMongoError:
        logging.exception("Learning state retrieval failed")
        return RaiseJSONErr("Unable to load learning progress", 500)


@learning_api.post("/favorites")
def update_favorite():
    data, error_response = _body()
    if error_response:
        return error_response
    career_id = _career_id(data)
    if career_id is None or not isinstance(data.get("favorite"), bool):
        return RaiseJSONErr("Provide a valid career_id and favorite boolean", 400)
    user_id, error_response = _account(data)
    if error_response:
        return error_response
    try:
        _ensure_document(user_id)
        operation = {"$addToSet": {"favorites": career_id}} if data["favorite"] else {
            "$pull": {"favorites": career_id}
        }
        career_learning.update_one({"user_id": user_id}, operation)
        return json_response({
            "success": True,
            "favorites": _get_state(user_id)["favorites"],
        })
    except PyMongoError:
        logging.exception("Favorite update failed")
        return RaiseJSONErr("Unable to save favorite", 500)


@learning_api.post("/roadmaps")
def update_saved_roadmap():
    data, error_response = _body()
    if error_response:
        return error_response
    career_id = _career_id(data)
    if career_id is None or not isinstance(data.get("saved"), bool):
        return RaiseJSONErr("Provide a valid career_id and saved boolean", 400)
    user_id, error_response = _account(data)
    if error_response:
        return error_response
    try:
        _ensure_document(user_id)
        operation = {"$addToSet": {"saved_roadmaps": career_id}} if data["saved"] else {
            "$pull": {"saved_roadmaps": career_id}
        }
        career_learning.update_one({"user_id": user_id}, operation)
        return json_response({
            "success": True,
            "saved_roadmaps": _get_state(user_id)["saved_roadmaps"],
        })
    except PyMongoError:
        logging.exception("Saved roadmap update failed")
        return RaiseJSONErr("Unable to save learning roadmap", 500)


@learning_api.put("/progress")
def update_skill_progress():
    data, error_response = _body()
    if error_response:
        return error_response
    career_id = _career_id(data)
    skill = data.get("skill")
    completed = data.get("completed")
    if career_id is None or not isinstance(skill, str) or not isinstance(completed, bool):
        return RaiseJSONErr("Provide a valid career_id, skill, and completed boolean", 400)
    career = find_career(career_id)
    canonical_skill = next(
        (
            required for required in career["required_skills"]
            if required.casefold() == skill.strip().casefold()
        ),
        None,
    )
    if canonical_skill is None:
        return RaiseJSONErr("Skill is not part of this career roadmap", 400)
    user_id, error_response = _account(data)
    if error_response:
        return error_response
    try:
        _ensure_document(user_id)
        skills_path = f"completed_skills.{career_id}"
        operation = (
            {"$addToSet": {skills_path: canonical_skill}}
            if completed
            else {"$pull": {skills_path: canonical_skill}}
        )
        career_learning.update_one({"user_id": user_id}, operation)
        return json_response({
            "success": True,
            "completed_skills": _get_state(user_id)["completed_skills"],
        })
    except PyMongoError:
        logging.exception("Skill progress update failed")
        return RaiseJSONErr("Unable to update skill progress", 500)


@learning_api.post("/quiz-results")
def save_quiz_result():
    data, error_response = _body()
    if error_response:
        return error_response
    career_ids = data.get("career_ids")
    if (
        not isinstance(career_ids, list)
        or not 1 <= len(career_ids) <= 5
        or not all(
            isinstance(career_id, int)
            and not isinstance(career_id, bool)
            and career_id in careers.values()
            for career_id in career_ids
        )
        or len(set(career_ids)) != len(career_ids)
    ):
        return RaiseJSONErr("Provide 1 to 5 distinct valid career IDs", 400)
    user_id, error_response = _account(data)
    if error_response:
        return error_response
    result = {
        "career_ids": career_ids,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        _ensure_document(user_id)
        career_learning.update_one(
            {"user_id": user_id},
            {"$push": {"quiz_results": {"$each": [result], "$slice": -20}}},
        )
        return json_response({"success": True, "quiz_results": _get_state(user_id)["quiz_results"]})
    except PyMongoError:
        logging.exception("Quiz result save failed")
        return RaiseJSONErr("Unable to save quiz result", 500)
