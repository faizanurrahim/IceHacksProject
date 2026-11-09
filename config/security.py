import json
import logging
import os
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from bson import ObjectId
from Nexa.nserver import Response, request

from config.ERR import RaiseJSONErr

SESSION_COOKIE = "careerpath_session"
SESSION_MAX_AGE = 24 * 60 * 60


def jwt_secret() -> str | None:
    secret = os.getenv("JWT_SECRET")
    if not secret or len(secret) < 32:
        logging.error("JWT_SECRET must be configured with at least 32 characters")
        return None
    return secret


def create_session_token(user_id: str) -> str:
    secret = jwt_secret()
    if not secret:
        raise RuntimeError("JWT_SECRET is required")
    return jwt.encode(
        {
            "sub": user_id,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(seconds=SESSION_MAX_AGE),
        },
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


def session_cookie(token: str) -> str:
    cookie = (
        f"{SESSION_COOKIE}={token}; Path=/; Max-Age={SESSION_MAX_AGE}; "
        "HttpOnly; SameSite=Lax"
    )
    secure_setting = os.getenv("COOKIE_SECURE")
    secure = (
        secure_setting.strip().lower() in {"1", "true", "yes"}
        if secure_setting is not None
        else os.getenv("APP_ENV", "").strip().lower() == "production"
    )
    if secure:
        cookie += "; Secure"
    return cookie


def clear_session_cookie() -> str:
    cookie = f"{SESSION_COOKIE}=; Path=/; Max-Age=0; HttpOnly; SameSite=Lax"
    secure_setting = os.getenv("COOKIE_SECURE")
    secure = (
        secure_setting.strip().lower() in {"1", "true", "yes"}
        if secure_setting is not None
        else os.getenv("APP_ENV", "").strip().lower() == "production"
    )
    if secure:
        cookie += "; Secure"
    return cookie


def authenticate_request(data: Any = None) -> tuple[str | None, Any | None]:
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
    return user_id, None


def is_valid_session() -> bool:
    token = request.cookies.get(SESSION_COOKIE)
    secret = jwt_secret()
    if not token or not secret:
        return False
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
    except jwt.InvalidTokenError:
        return False
    return isinstance(payload.get("sub"), str) and ObjectId.is_valid(payload["sub"])
