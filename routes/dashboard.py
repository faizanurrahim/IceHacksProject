import logging

from bson import ObjectId
from pymongo.errors import PyMongoError

from Nexa import Blueprint
from Nexa.nserver import request

from config.ERR import RaiseJSONErr
from config.db import users, career_profiles
from config.recommendations import recommend_careers
from config.security import authenticate_request, json_response

dashboard_api = Blueprint("dashboardAPI", "/api/v1")


def dashboard_data(user_id):
    user = users.find_one({"_id": ObjectId(user_id)})
    if user is None:
        return None, RaiseJSONErr("User account not found", 404)

    profile = career_profiles.find_one({"user_id": user_id})
    description = profile.get("description", {}) if profile else {}
    completed_fields = sum(
        bool(description.get(field))
        for field in ("education", "subjects", "interests", "skills", "preferred_careers")
    )
    return {
        "success": True,
        "user": {
            "id": user_id,
            "full_name": user.get("full_name", ""),
            "email": user.get("email", ""),
            "is_verified": user.get("is_verified", False),
            "created_at": user.get("created_at").isoformat()
            if user.get("created_at") else None,
        },
        "profile": {
            "completed": completed_fields == 5,
            "completion_percentage": completed_fields * 20,
            "description": description,
        },
        "recommendations": recommend_careers(description) if description else [],
    }, None


@dashboard_api.route("/dash", methods=["GET", "POST"])
def get_dashboard():
    try:
        data = request.json if request.method == "POST" else None
        if data is not None and not isinstance(data, dict):
            return RaiseJSONErr("Invalid JSON request", 400)
        user_id, auth_error = authenticate_request(data)
        if auth_error:
            return auth_error
        result, error_response = dashboard_data(user_id)
        if error_response:
            return error_response
        if result is None:
            return RaiseJSONErr("Unable to load dashboard", 500)
        return json_response(result)
    except PyMongoError:
        logging.exception("Dashboard API error")
        return RaiseJSONErr("Database operation failed", 500)


@dashboard_api.get("/recommendations")
def get_recommendations():
    user_id, auth_error = authenticate_request()
    if auth_error:
        return auth_error
    try:
        if users.find_one({"_id": ObjectId(user_id)}, {"_id": 1}) is None:
            return RaiseJSONErr("User account not found", 404)
        profile = career_profiles.find_one({"user_id": user_id})
        if not profile:
            return RaiseJSONErr("Complete your career profile to get recommendations", 409)
        return json_response({
            "success": True,
            "recommendations": recommend_careers(profile.get("description", {})),
        })
    except PyMongoError:
        logging.exception("MongoDB recommendations error")
        return RaiseJSONErr("Database operation failed", 500)