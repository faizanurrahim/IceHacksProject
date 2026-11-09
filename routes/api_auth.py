import logging
import re
from datetime import datetime, timezone

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
from bson import ObjectId
from pymongo.errors import DuplicateKeyError, PyMongoError
from Nexa import Blueprint
from Nexa.nserver import request

from config.ERR import RaiseJSONErr
from config.db import career_learning, career_profiles, client, users
from config.security import (
    authenticate_request,
    clear_session_cookie,
    create_session_token,
    json_response,
    jwt_secret,
    session_cookie,
)

authapi = Blueprint("authAPI", "/api/v1/auth")
password_hasher = PasswordHasher()


def _session_response(user: dict, message: str, status: int = 200):
    user_data = {
        "id": str(user["_id"]),
        "full_name": user["full_name"],
        "email": user["email"],
        "is_verified": user.get("is_verified", False),
    }
    return json_response(
        {"success": True, "message": message, "user": user_data},
        status=status,
        headers={"Set-Cookie": session_cookie(create_session_token(user_data["id"]))},
    )


@authapi.post("/sign-up")
def sign_up():
    try:
        data = request.json
        if not isinstance(data, dict):
            return RaiseJSONErr("Invalid JSON request", 400)

        email = data.get("email")
        password = data.get("password")
        name = data.get("full-name")
        if not isinstance(email, str) or not isinstance(password, str) or not isinstance(name, str):
            return RaiseJSONErr("All fields are required", 400)

        email = email.strip().lower()
        name = name.strip()
        if not email or not password or not name:
            return RaiseJSONErr("All fields are required", 400)
        if len(email) > 254 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
            return RaiseJSONErr("Invalid email address", 400)
        if len(name) > 100:
            return RaiseJSONErr("Name must be 100 characters or fewer", 400)
        if len(password) < 8 or len(password) > 128:
            return RaiseJSONErr("Password must contain 8 to 128 characters", 400)
        if not jwt_secret():
            return RaiseJSONErr("Authentication configuration error", 500)

        user = {
            "full_name": name,
            "email": email,
            "password_hash": password_hasher.hash(password),
            "created_at": datetime.now(timezone.utc),
            "is_verified": False,
        }
        result = users.insert_one(user)
        user["_id"] = result.inserted_id
        return _session_response(user, "Account created successfully", 201)
    except DuplicateKeyError:
        return RaiseJSONErr("Email already registered", 409)
    except PyMongoError:
        logging.exception("MongoDB signup error")
        return RaiseJSONErr("Database operation failed", 500)
    except Exception:
        logging.exception("Signup error")
        return RaiseJSONErr("Internal server error", 500)


@authapi.post("/login")
def login():
    try:
        data = request.json
        if not isinstance(data, dict):
            return RaiseJSONErr("Invalid JSON request", 400)

        email = data.get("email")
        password = data.get("password")
        if not isinstance(email, str) or not isinstance(password, str):
            return RaiseJSONErr("Email and password are required", 400)
        email = email.strip().lower()
        if not email or len(email) > 254 or not password:
            return RaiseJSONErr("Email and password are required", 400)
        if len(password) > 128:
            return RaiseJSONErr("Password must be 128 characters or fewer", 400)

        user = users.find_one({"email": email})
        if user is None:
            return RaiseJSONErr("Invalid email or password", 401)
        try:
            password_hasher.verify(user["password_hash"], password)
        except VerifyMismatchError:
            return RaiseJSONErr("Invalid email or password", 401)
        except (VerificationError, InvalidHashError):
            logging.exception("Password hash verification failed")
            return RaiseJSONErr("Unable to authenticate account", 500)

        if password_hasher.check_needs_rehash(user["password_hash"]):
            users.update_one(
                {"_id": user["_id"]},
                {"$set": {"password_hash": password_hasher.hash(password)}},
            )
        return _session_response(user, "Login successful")
    except PyMongoError:
        logging.exception("MongoDB login error")
        return RaiseJSONErr("Database operation failed", 500)
    except Exception:
        logging.exception("Login error")
        return RaiseJSONErr("Internal server error", 500)


@authapi.post("/logout")
def logout():
    return json_response(
        {"success": True, "message": "Logged out"},
        headers={"Set-Cookie": clear_session_cookie()},
    )


@authapi.get("/me")
def current_user():
    user_id, error_response = authenticate_request()
    if error_response:
        return error_response
    try:
        user = users.find_one(
            {"_id": ObjectId(user_id)},
            {"full_name": 1, "email": 1, "is_verified": 1, "created_at": 1},
        )
        if user is None:
            return RaiseJSONErr("User account not found", 404)
        return json_response({
            "success": True,
            "user": {
                "id": user_id,
                "full_name": user.get("full_name", ""),
                "email": user.get("email", ""),
                "is_verified": user.get("is_verified", False),
                "created_at": user.get("created_at").isoformat()
                if user.get("created_at") else None,
            },
        })
    except PyMongoError:
        logging.exception("MongoDB current user error")
        return RaiseJSONErr("Database operation failed", 500)


@authapi.delete("/account")
def delete_account():
    data = request.json
    if not isinstance(data, dict):
        return RaiseJSONErr("Invalid JSON request", 400)
    if data.get("confirmation") != "DELETE":
        return RaiseJSONErr("Type DELETE to confirm account removal", 400)
    password = data.get("password")
    if not isinstance(password, str) or not password:
        return RaiseJSONErr("Password is required to delete your account", 400)

    user_id, error_response = authenticate_request(data)
    if error_response:
        return error_response
    try:
        user = users.find_one({"_id": ObjectId(user_id)})
        if user is None:
            return RaiseJSONErr("User account not found", 404)
        try:
            password_hasher.verify(user["password_hash"], password)
        except VerifyMismatchError:
            return RaiseJSONErr("Incorrect password", 401)
        except (VerificationError, InvalidHashError):
            logging.exception("Account deletion hash verification failed")
            return RaiseJSONErr("Unable to verify account password", 500)

        def remove_account(session):
            career_profiles.delete_one({"user_id": user_id}, session=session)
            career_learning.delete_one({"user_id": user_id}, session=session)
            result = users.delete_one({"_id": ObjectId(user_id)}, session=session)
            if result.deleted_count != 1:
                raise RuntimeError("User account no longer exists")
            return result.deleted_count

        with client.start_session() as mongo_session:
            mongo_session.with_transaction(remove_account)
        return json_response(
            {"success": True, "message": "Account deleted"},
            headers={"Set-Cookie": clear_session_cookie()},
        )
    except RuntimeError:
        return RaiseJSONErr("User account not found", 404)
    except PyMongoError:
        logging.exception("MongoDB account deletion error")
        return RaiseJSONErr("Account deletion failed", 500)
