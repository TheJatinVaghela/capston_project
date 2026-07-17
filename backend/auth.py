"""JWT authentication helpers."""

from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash

import config
import database as db


def hash_password(password):
    return generate_password_hash(password)


def verify_password(password_hash, password):
    return check_password_hash(password_hash, password)


def create_token(user_id, email):
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=config.JWT_EXPIRY_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, config.SECRET_KEY, algorithm="HS256")


def decode_token(token):
    return jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])


def get_bearer_token():
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:].strip()
    return None


def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = get_bearer_token()
        if not token:
            return jsonify({"error": "Authentication required"}), 401
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        user = db.get_user_by_id(payload["sub"])
        if not user:
            return jsonify({"error": "User not found"}), 401
        request.current_user = user
        return f(*args, **kwargs)

    return wrapper


def require_business_owner(f):
    """Expects business_id in URL kwargs; ensures current user owns it."""

    @wraps(f)
    @require_auth
    def wrapper(*args, **kwargs):
        business_id = kwargs.get("business_id")
        biz = db.get_business_by_id(business_id)
        if not biz:
            return jsonify({"error": "Business not found"}), 404
        if biz["owner_id"] != request.current_user["id"]:
            return jsonify({"error": "Forbidden"}), 403
        request.current_business = biz
        return f(*args, **kwargs)

    return wrapper
