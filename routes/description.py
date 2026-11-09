import logging
from datetime import datetime, timezone

from bson import ObjectId
from pymongo.errors import PyMongoError
from Nexa import Blueprint
from Nexa.nserver import request

from config.ERR import RaiseJSONErr
from config.db import career_profiles, users
from config.profile import validate_description
from config.security import authenticate_request, json_response

description_api = Blueprint("descriptionAPI", "/api/v1")


def save_profile(data):
    if not isinstance(data, dict):
        return None, RaiseJSONErr("Invalid JSON request", 400)
    user_id, auth_error = authenticate_request(data)
    if auth_error:
        return None, auth_error

    answers, validation_error = validate_description(data.get("description"))
    if validation_error:
        return None, RaiseJSONErr(validation_error, 400)

    try:
        if users.find_one({"_id": ObjectId(user_id)}, {"_id": 1}) is None:
            return None, RaiseJSONErr("User account not found", 404)
        now = datetime.now(timezone.utc)
        career_profiles.update_one(
            {"user_id": user_id},
            {
                "$set": {"description": answers, "updated_at": now},
                "$setOnInsert": {"user_id": user_id, "created_at": now},
            },
            upsert=True,
        )
        return user_id, None
    except PyMongoError:
        logging.exception("MongoDB profile save error")
        return None, RaiseJSONErr("Database operation failed", 500)


@description_api.post("/discription")
def save_description():
    user_id, error_response = save_profile(request.json)
    if error_response:
        return error_response
    return json_response({
        "success": True,
        "message": "Career profile saved successfully",
        "user_id": user_id,
    })


@description_api.route("/profile", methods=["GET", "PUT"])
def profile():
    if request.method == "GET":
        user_id, error_response = authenticate_request()
        if error_response:
            return error_response
        try:
            if users.find_one({"_id": ObjectId(user_id)}, {"_id": 1}) is None:
                return RaiseJSONErr("User account not found", 404)
            saved_profile = career_profiles.find_one({"user_id": user_id})
            return json_response({
                "success": True,
                "profile": saved_profile.get("description", {}) if saved_profile else {},
                "completed": bool(saved_profile),
            })
        except PyMongoError:
            logging.exception("MongoDB profile retrieval error")
            return RaiseJSONErr("Database operation failed", 500)

    user_id, error_response = save_profile(request.json)
    if error_response:
        return error_response
    return json_response({
        "success": True,
        "message": "Career profile updated successfully",
        "user_id": user_id,
    })
