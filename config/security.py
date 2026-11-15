import json
import hashlib
import logging
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from bson import ObjectId
from pymongo.errors import PyMongoError
from Nexa.nserver import Response, request

from config.ERR import RaiseJSONErr
from config.db import persistent_sessions

SESSION_COOKIE = "careerpath_session"
SESSION_MAX_AGE = 24 * 60 * 60
REMEMBER_SESSION_MAX_AGE = 30 * 24 * 60 * 60


def jwt_secret() -> str | None:
    secret = os.getenv("JWT_SECRET")
    if not secret or len(secret) < 32:
        logging.error("JWT_SECRET must be configured with at least 32 characters")
        return None
    return secret


def create_session_token(user_id: str, remember_me: bool = False) -> str:
    secret = jwt_secret()
    if not secret:
        raise RuntimeError("JWT_SECRET is required")
    now = datetime.now(timezone.utc)
    max_age = REMEMBER_SESSION_MAX_AGE if remember_me else SESSION_MAX_AGE
    payload = {
        "sub": user_id,
        "iat": now,
        "exp": now + timedelta(seconds=max_age),
    }
    if remember_me:
        payload["remember_me"] = True
        payload["jti"] = secrets.token_urlsafe(32)
    return jwt.encode(
        payload,
        secret,
        algorithm="HS256",
    )


def json_response(
    payload: dict[str, Any],
    status: int = 200,
    headers: dict[str, str] | None = None,
) -> Response:
    response_headers = {"Cache-Control": "no-store"}
    if headers:
        response_headers.update(headers)
    return Response(
        json.dumps(payload, ensure_ascii=False),
        status=status,
        content_type="application/json; charset=utf-8",
        headers=response_headers,
    )


def secure_cookie_enabled() -> bool:
    if os.getenv("APP_ENV", "").strip().lower() == "production":
        return True
    return os.getenv("COOKIE_SECURE", "").strip().lower() in {"1", "true", "yes"}


def session_cookie(token: str, remember_me: bool = False) -> str:
    max_age = REMEMBER_SESSION_MAX_AGE if remember_me else SESSION_MAX_AGE
    cookie = (
        f"{SESSION_COOKIE}={token}; Path=/; Max-Age={max_age}; "
        "HttpOnly; SameSite=Lax"
    )
    if secure_cookie_enabled():
        cookie += "; Secure"
    return cookie


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def persist_session_token(token: str, user_id: str, remember_me: bool) -> None:
    if not remember_me:
        return
    now = datetime.now(timezone.utc)
    persistent_sessions.insert_one({
        "token_hash": _token_hash(token),
        "user_id": user_id,
        "created_at": now,
        "expires_at": now + timedelta(seconds=REMEMBER_SESSION_MAX_AGE),
    })


def revoke_persistent_session(token: str | None) -> None:
    if not token:
        return
    secret = jwt_secret()
    if not secret:
        return
    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            options={"verify_exp": False},
        )
    except jwt.InvalidTokenError:
        return
    if payload.get("remember_me") is True:
        persistent_sessions.delete_one({"token_hash": _token_hash(token)})


def clear_session_cookie() -> str:
    cookie = f"{SESSION_COOKIE}=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax"
    if secure_cookie_enabled():
        cookie += "; Secure"
    return cookie


def get_request_token(data: Any = None) -> str | None:
    token = request.cookies.get(SESSION_COOKIE)

    authorization = next(
        (
            value
            for key, value in request.headers.items()
            if key.lower() == "authorization"
        ),
        "",
    )
    if not token and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()

    # Accept legacy clients while the browser frontend uses the HttpOnly cookie.
    if not token and isinstance(data, dict):
        legacy_token = data.get("token")
        if isinstance(legacy_token, str):
            token = legacy_token
    return token


def authenticate_request(data: Any = None) -> tuple[str | None, Any | None]:
    token = get_request_token(data)

    if not token:
        return None, RaiseJSONErr("Authentication required", 401)

    secret = jwt_secret()
    if not secret:
        return None, RaiseJSONErr("Authentication configuration error", 500)

    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None, RaiseJSONErr("Session expired. Please log in again.", 401)
    except jwt.InvalidTokenError:
        return None, RaiseJSONErr("Invalid authentication token", 401)

    user_id = payload.get("sub")
    if not isinstance(user_id, str) or not ObjectId.is_valid(user_id):
        return None, RaiseJSONErr("Invalid user identity", 401)
    if payload.get("remember_me") is True:
        if not isinstance(payload.get("jti"), str):
            return None, RaiseJSONErr("Invalid persistent session", 401)
        try:
            session = persistent_sessions.find_one({
                "token_hash": _token_hash(token),
                "user_id": user_id,
                "expires_at": {"$gt": datetime.now(timezone.utc)},
            })
        except PyMongoError:
            logging.exception("Persistent session validation failed")
            return None, RaiseJSONErr("Unable to validate session", 500)
        if session is None:
            return None, RaiseJSONErr("Session expired or revoked", 401)
    return user_id, None


def is_valid_session() -> bool:
    user_id, error_response = authenticate_request()
    return user_id is not None and error_response is None
