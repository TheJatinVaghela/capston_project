"""
SupportFlow SaaS API — multi-tenant customer chatbot.
"""

import json
import logging
import os
import uuid
from datetime import datetime, timezone

from flask import Flask, request, jsonify, send_from_directory, Response, stream_with_context

import config
import database as db
import security
from auth import (
    require_auth,
    require_business_owner,
    hash_password,
    verify_password,
    create_token,
    decode_token,
)
from chatbot import chat, stream_chat, get_chatbot
import jwt as pyjwt

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

config.validate_security_config()

app = Flask(__name__)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
FRONTEND_DIST = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend-react", "dist")
)

DASHBOARD_ORIGINS = {
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:5175",
    "http://127.0.0.1:5175",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    config.FRONTEND_URL,
    config.PUBLIC_BASE_URL,
}


def _is_local_dev_origin(origin: str) -> bool:
    """Allow Vite (and similar) on any localhost port while developing."""
    if config.ENVIRONMENT != "development":
        return False
    o = security.normalize_origin(origin or "")
    return o.startswith("http://localhost:") or o.startswith("http://127.0.0.1:")


def _is_tunnel_origin(origin: str) -> bool:
    """Allow common tunnel hosts when sharing the app from a laptop."""
    if not config.ALLOW_TUNNEL_ORIGINS:
        return False
    o = security.normalize_origin(origin or "").lower()
    markers = (
        "ngrok-free.app",
        "ngrok.io",
        "ngrok.app",
        "trycloudflare.com",
        "loca.lt",
        "localhost.run",
    )
    return any(m in o for m in markers)


def now_utc():
    return datetime.now(timezone.utc).isoformat()


def can_use_embed(biz):
    return (biz.get("subscription_status") or "free") in ("active", "trialing")


def can_preview_chat(biz):
    status = biz.get("subscription_status") or "free"
    if status in ("active", "trialing"):
        return True, None
    if (biz.get("preview_chat_count") or 0) >= config.FREE_PREVIEW_CHAT_LIMIT:
        return False, "Free preview limit reached. Subscribe to continue."
    return True, None


def _user_public(user):
    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "created_at": user.get("created_at"),
    }


def _account_plan_summary(user_id):
    businesses = db.get_businesses_for_user(user_id)
    account_plan = config.highest_account_plan(businesses)
    limits = config.plan_limits(account_plan)
    return {
        "account_plan": account_plan,
        "business_count": len(businesses),
        "max_businesses": limits["max_businesses"],
        "can_create_business": len(businesses) < limits["max_businesses"],
        "limits": limits,
        "businesses": businesses,
    }


def _normalize_chat_colors(raw) -> dict:
    """Accept only safe hex colors for known keys."""
    import re

    if not isinstance(raw, dict):
        return {}
    out = {}
    for key in ("primary", "header", "user_bubble", "accent"):
        val = (raw.get(key) or "").strip()
        if re.fullmatch(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})", val):
            out[key] = val
    return out


def _generic_error(message="Request failed", status=400):
    return jsonify({"error": message}), status


def _client_error_message(exc):
    """Log full exception; return a safe client message (more detail in development)."""
    logger.exception("Request failed: %s", exc)
    try:
        import stripe

        if isinstance(exc, stripe.error.StripeError):
            msg = getattr(exc, "user_message", None) or str(exc)
            if msg and "sk_" not in msg and "rk_" not in msg:
                return msg
    except Exception:
        pass
    if not config.IS_PRODUCTION:
        text = str(exc)
        if text and "sk_" not in text and len(text) < 300:
            return text
    return "Something went wrong. Please try again."


def _widget_key_from_request():
    """Read widget key from headers/query only — never parse JSON body here (CORS/after_request safe)."""
    return (
        (request.headers.get("X-Widget-Key") or "").strip()
        or (request.args.get("key") or "").strip()
    )


def _origin_permitted(origin: str) -> bool:
    origin = security.normalize_origin(origin)
    if not origin:
        return True
    if origin in DASHBOARD_ORIGINS:
        return True
    if _is_local_dev_origin(origin):
        return True
    if _is_tunnel_origin(origin):
        return True
    key = _widget_key_from_request()
    if key:
        biz = db.get_business_by_widget_key(key)
        if not biz:
            return False
        allowed = biz.get("allowed_origins") or []
        return security.origin_allowed(
            origin, allowed, strict=config.WIDGET_STRICT_ORIGINS
        )
    # Public demo / dashboard-only routes: origin must be dashboard
    return False


@app.before_request
def _security_before_request():
    if request.method == "OPTIONS":
        origin = request.headers.get("Origin")
        if origin and not _origin_permitted(origin):
            return jsonify({"error": "Origin not allowed"}), 403
        return ("", 204)


@app.after_request
def _security_after_request(response):
    origin = request.headers.get("Origin")
    if origin and _origin_permitted(origin):
        response.headers["Access-Control-Allow-Origin"] = security.normalize_origin(
            origin
        )
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Vary"] = "Origin"
        response.headers["Access-Control-Allow-Headers"] = (
            "Authorization, Content-Type, X-Widget-Key"
        )
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, PATCH, DELETE, OPTIONS"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


def _rate_limit_or_429(bucket: str, limit: int, window_sec: float = 60.0):
    ip = security.client_ip(request)
    if not security.limiter.allow(f"{bucket}:{ip}", limit, window_sec):
        return jsonify({"error": "Rate limit exceeded. Try again shortly."}), 429
    return None


def _validate_session_id(session_id: str):
    if not session_id or len(session_id) > security.MAX_SESSION_ID_CHARS:
        return None
    # Prefer UUID-like ids; reject path/injection junk
    if not all(c.isalnum() or c in "-_" for c in session_id):
        return None
    return session_id


def _enforce_widget_origin(biz):
    origin = request.headers.get("Origin")
    if not origin:
        return None
    allowed = biz.get("allowed_origins") or []
    if not security.origin_allowed(
        origin, allowed, strict=config.WIDGET_STRICT_ORIGINS
    ):
        return "Origin not allowed for this widget", 403
    return None


# ── Health ─────────────────────────────────────────────────────────────────


@app.route("/", methods=["GET"])
def home():
    # Always serve the React app when built (tunnel / shared link).
    # Status JSON lives at /health so browsers never get API JSON on "/".
    index = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.isfile(index):
        return send_from_directory(FRONTEND_DIST, "index.html")
    return jsonify(
        {
            "status": "running",
            "product": config.PRODUCT_NAME,
            "version": "4.0.0",
            "frontend_built": False,
            "error": "Frontend not built. Run: cd frontend-react && npm run build",
            "features": [
                "Multi-tenant businesses",
                "JWT auth",
                "Tenant knowledge base",
                "Support-only AI guardrails",
                "Stripe subscriptions",
                "Embeddable widget",
                "Ollama AI",
            ],
        }
    ), 200


@app.route("/health", methods=["GET"])
def health():
    index = os.path.join(FRONTEND_DIST, "index.html")
    return jsonify(
        {
            "status": "running",
            "product": config.PRODUCT_NAME,
            "version": "4.0.0",
            "frontend_built": os.path.isfile(index),
            "features": [
                "Multi-tenant businesses",
                "JWT auth",
                "Tenant knowledge base",
                "Support-only AI guardrails",
                "Stripe subscriptions",
                "Embeddable widget",
                "Ollama AI",
            ],
        }
    ), 200


# ── Auth ───────────────────────────────────────────────────────────────────


@app.route("/auth/register", methods=["POST"])
def register():
    limited = _rate_limit_or_429("auth", config.RATE_LIMIT_AUTH)
    if limited:
        return limited
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    name = (data.get("name") or "").strip()
    business_name = (data.get("business_name") or "").strip()
    website = (data.get("website") or "").strip()
    description = (data.get("description") or "").strip()

    if not email or not password or not name:
        return jsonify({"error": "email, password, and name are required"}), 400
    pw_err = security.validate_password(password)
    if pw_err:
        return jsonify({"error": pw_err}), 400
    if db.get_user_by_email(email):
        return jsonify({"error": "Email already registered"}), 409

    user = db.create_user(email, hash_password(password), name)
    biz = None
    if business_name:
        biz = db.create_business(
            user["id"], business_name, website=website, description=description
        )

    token = create_token(user["id"], user["email"])
    return jsonify(
        {
            "token": token,
            "user": _user_public(user),
            "business": db.public_business_view(biz) if biz else None,
        }
    ), 201


@app.route("/auth/login", methods=["POST"])
def login():
    limited = _rate_limit_or_429("auth", config.RATE_LIMIT_AUTH)
    if limited:
        return limited
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    user = db.get_user_by_email(email)
    if not user or not verify_password(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password"}), 401
    token = create_token(user["id"], user["email"])
    businesses = db.get_businesses_for_user(user["id"])
    return jsonify(
        {
            "token": token,
            "user": _user_public(user),
            "businesses": [db.public_business_view(b) for b in businesses],
        }
    ), 200


@app.route("/auth/me", methods=["GET"])
@require_auth
def me():
    summary = _account_plan_summary(request.current_user["id"])
    return jsonify(
        {
            "user": _user_public(request.current_user),
            "businesses": [db.public_business_view(b) for b in summary["businesses"]],
            "account_plan": summary["account_plan"],
            "business_count": summary["business_count"],
            "max_businesses": summary["max_businesses"],
            "can_create_business": summary["can_create_business"],
            "plan_limits": summary["limits"],
        }
    ), 200


# ── Businesses ─────────────────────────────────────────────────────────────


@app.route("/businesses", methods=["GET"])
@require_auth
def list_businesses():
    summary = _account_plan_summary(request.current_user["id"])
    return jsonify(
        {
            "businesses": [db.public_business_view(b) for b in summary["businesses"]],
            "account_plan": summary["account_plan"],
            "business_count": summary["business_count"],
            "max_businesses": summary["max_businesses"],
            "can_create_business": summary["can_create_business"],
        }
    ), 200


@app.route("/businesses", methods=["POST"])
@require_auth
def create_business():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "Business name is required"}), 400

    summary = _account_plan_summary(request.current_user["id"])
    if not summary["can_create_business"]:
        plan_name = summary["account_plan"].title()
        return jsonify(
            {
                "error": (
                    f"Your {plan_name} plan allows up to "
                    f"{summary['max_businesses']} business"
                    f"{'es' if summary['max_businesses'] != 1 else ''}. "
                    "Upgrade on Billing to add more."
                ),
                "account_plan": summary["account_plan"],
                "business_count": summary["business_count"],
                "max_businesses": summary["max_businesses"],
            }
        ), 403

    biz = db.create_business(
        request.current_user["id"],
        name,
        website=(data.get("website") or "").strip(),
        description=(data.get("description") or "").strip(),
    )
    return jsonify({"business": db.public_business_view(biz)}), 201


@app.route("/businesses/<business_id>", methods=["GET"])
@require_business_owner
def get_business(business_id):
    return jsonify({"business": db.public_business_view(request.current_business)}), 200


@app.route("/businesses/<business_id>", methods=["PUT", "PATCH"])
@require_business_owner
def update_business(business_id):
    data = request.get_json(silent=True) or {}
    fields = {}
    for key in ("name", "website", "description"):
        if key in data:
            fields[key] = (data[key] or "").strip()
    if "knowledge" in data and isinstance(data["knowledge"], dict):
        knowledge = data["knowledge"]
        # Keep business_info name in sync
        if fields.get("name"):
            knowledge.setdefault("business_info", {})
            knowledge["business_info"]["name"] = fields["name"]
        if "website" in fields:
            knowledge.setdefault("business_info", {})
            knowledge["business_info"]["website"] = fields["website"]
        if "description" in fields:
            knowledge.setdefault("business_info", {})
            knowledge["business_info"]["description"] = fields["description"]
        fields["knowledge"] = knowledge
    biz = db.update_business(business_id, **fields)
    return jsonify({"business": db.public_business_view(biz)}), 200


def _knowledge_word_limit_response(text: str, effective: str, max_words: int):
    """
    Enforce plan knowledge word limits in one place.

    Returns (word_count, error_response_or_None).
    error_response is a (jsonify(...), status) tuple when over limit.
    """
    word_count = config.count_words(text)
    if word_count <= max_words:
        return word_count, None
    return word_count, (
        jsonify(
            {
                "error": (
                    f"Knowledge is {word_count} words; your "
                    f"{effective.title()} plan allows {max_words} words. "
                    "Shorten the text or upgrade on Billing."
                ),
                "word_count": word_count,
                "max_knowledge_words": max_words,
                "effective_plan": effective,
            }
        ),
        403,
    )


def _seed_knowledge_business_info(knowledge: dict, biz: dict) -> dict:
    """Ensure knowledge embeds basic business identity fields."""
    info = knowledge.setdefault("business_info", {})
    if not isinstance(info, dict):
        info = {}
        knowledge["business_info"] = info
    info.setdefault("name", biz["name"])
    info.setdefault("website", biz.get("website") or "")
    info.setdefault("description", biz.get("description") or "")
    return knowledge


@app.route("/businesses/<business_id>/knowledge", methods=["PUT"])
@require_business_owner
def update_knowledge(business_id):
    data = request.get_json(silent=True) or {}
    biz = request.current_business
    effective = config.effective_plan_id(biz.get("plan"), biz.get("subscription_status"))
    limits = config.plan_limits(effective)
    max_words = limits["max_knowledge_words"]

    # Free-text knowledge (preferred)
    if "text" in data or "knowledge_text" in data:
        text = data.get("text")
        if text is None:
            text = data.get("knowledge_text")
        if not isinstance(text, str):
            return jsonify({"error": "text must be a string"}), 400
        text = security.sanitize_knowledge_text(text)
        word_count, limit_error = _knowledge_word_limit_response(
            text, effective, max_words
        )
        if limit_error:
            return limit_error
        warnings = security.knowledge_security_warnings(text)
        knowledge = _seed_knowledge_business_info(dict(biz.get("knowledge") or {}), biz)
        knowledge["text"] = text
        biz = db.update_business(business_id, knowledge=knowledge)
        return jsonify(
            {
                "business": db.public_business_view(biz),
                "warnings": warnings,
                "word_count": word_count,
                "max_knowledge_words": max_words,
            }
        ), 200

    # Legacy structured object
    knowledge = data.get("knowledge")
    if not isinstance(knowledge, dict):
        return jsonify({"error": "Provide text (string) or knowledge (object)"}), 400
    word_count = None
    if isinstance(knowledge.get("text"), str):
        knowledge["text"] = security.sanitize_knowledge_text(knowledge["text"])
        word_count, limit_error = _knowledge_word_limit_response(
            knowledge["text"], effective, max_words
        )
        if limit_error:
            return limit_error
    warnings = security.knowledge_security_warnings(knowledge.get("text") or "")
    knowledge = _seed_knowledge_business_info(knowledge, biz)
    info = knowledge.get("business_info") or {}
    biz = db.update_business(
        business_id,
        knowledge=knowledge,
        name=info.get("name") or biz["name"],
        website=info.get("website") or biz.get("website") or "",
        description=info.get("description") or biz.get("description") or "",
    )
    payload = {"business": db.public_business_view(biz), "warnings": warnings}
    if word_count is not None:
        payload["word_count"] = word_count
        payload["max_knowledge_words"] = max_words
    return jsonify(payload), 200


@app.route("/businesses/<business_id>/settings", methods=["PUT"])
@require_business_owner
def update_business_settings(business_id):
    """Paid businesses: AI model + widget allowed origins + Premium chat colors."""
    data = request.get_json(silent=True) or {}
    biz = request.current_business
    fields = {}
    effective = config.effective_plan_id(biz.get("plan"), biz.get("subscription_status"))
    limits = config.plan_limits(effective)

    if "allowed_origins" in data:
        origins = security.parse_allowed_origins(data.get("allowed_origins"))
        cleaned = []
        for o in origins:
            if o.startswith("http://") or o.startswith("https://"):
                cleaned.append(security.normalize_origin(o))
        fields["allowed_origins"] = cleaned[:20]

    if "ai_model" in data:
        if not can_use_embed(biz):
            return jsonify(
                {
                    "error": "An active subscription is required to change AI model settings",
                    "subscription_status": biz.get("subscription_status"),
                }
            ), 402
        model = (data.get("ai_model") or "").strip().lower()
        allowed = {"mistral", "llama3", "neural-chat"}
        if model not in allowed:
            return jsonify(
                {"error": f"ai_model must be one of: {', '.join(sorted(allowed))}"}
            ), 400
        fields["ai_model"] = model

    if "chat_colors" in data:
        if not limits.get("chat_colors"):
            return jsonify(
                {
                    "error": "Custom chatbot colors are a Premium plan feature. Upgrade on Billing.",
                    "effective_plan": effective,
                }
            ), 402
        cleaned_colors = _normalize_chat_colors(data.get("chat_colors"))
        if not cleaned_colors:
            return jsonify(
                {
                    "error": "Provide at least one valid hex color "
                    "(primary, header, user_bubble, or accent)."
                }
            ), 400
        # Merge with existing saved colors
        existing = biz.get("chat_colors") or {}
        if not isinstance(existing, dict):
            existing = {}
        fields["chat_colors"] = {**existing, **cleaned_colors}

    if not fields:
        return jsonify({"error": "No settings to update"}), 400

    biz = db.update_business(business_id, **fields)
    return jsonify({"business": db.public_business_view(biz)}), 200


@app.route("/businesses/<business_id>/sessions", methods=["GET"])
@require_business_owner
def list_business_sessions(business_id):
    """Chat history: recent sessions for this business."""
    limit = min(request.args.get("limit", 40, type=int) or 40, 100)
    sessions = db.list_sessions_for_business(business_id, limit=limit)
    return jsonify({"sessions": sessions, "total": len(sessions)}), 200


@app.route("/businesses/<business_id>/sessions/<session_id>", methods=["DELETE"])
@require_business_owner
def delete_business_session(business_id, session_id):
    session_id = _validate_session_id(session_id)
    if not session_id:
        return jsonify({"error": "Invalid session_id"}), 400
    ok = db.delete_session(session_id, business_id=business_id)
    if not ok:
        return jsonify({"error": "Session not found"}), 404
    return jsonify({"status": "success", "deleted": session_id}), 200


@app.route("/businesses/<business_id>/widget-key", methods=["POST"])
@require_business_owner
def rotate_widget_key(business_id):
    if not can_use_embed(request.current_business):
        return jsonify(
            {
                "error": "Active subscription required for embed widget",
                "subscription_status": request.current_business.get(
                    "subscription_status"
                ),
            }
        ), 402
    biz = db.regenerate_widget_key(business_id)
    return jsonify({"business": db.public_business_view(biz)}), 200


@app.route("/businesses/public/<slug>", methods=["GET"])
def public_business(slug):
    biz = db.get_business_by_slug(slug)
    if not biz:
        return jsonify({"error": "Not found"}), 404
    knowledge = biz.get("knowledge") or {}
    return jsonify(
        {
            "name": biz["name"],
            "slug": biz["slug"],
            "website": biz.get("website"),
            "description": biz.get("description"),
            "business_info": knowledge.get("business_info", {}),
        }
    ), 200


# ── Chat ───────────────────────────────────────────────────────────────────


def _resolve_business_for_chat(data):
    """
    Resolve tenant from widget_key, authenticated business_id, or controlled public demo.
    Never falls back to an anonymous shared tenant without ALLOW_PUBLIC_DEMO.
    """
    widget_key = (data.get("widget_key") or _widget_key_from_request() or "").strip()
    if widget_key:
        biz = db.get_business_by_widget_key(widget_key)
        if not biz:
            return None, "Invalid widget key", 401
        if not can_use_embed(biz):
            return None, "Subscription required for widget chat", 402
        origin_err = _enforce_widget_origin(biz)
        if origin_err:
            return None, origin_err[0], origin_err[1]
        return biz, None, None

    business_id = (data.get("business_id") or "").strip()
    if business_id:
        biz = db.get_business_by_id(business_id)
        if not biz:
            return None, "Business not found", 404
        token = request.headers.get("Authorization", "")
        if not token.startswith("Bearer "):
            return None, "Authentication required for preview chat", 401
        try:
            payload = decode_token(token[7:].strip())
        except pyjwt.PyJWTError:
            return None, "Invalid token", 401
        if biz["owner_id"] != payload["sub"]:
            return None, "Forbidden", 403
        ok, reason = can_preview_chat(biz)
        if not ok:
            return None, reason, 402
        return biz, None, None

    # Controlled public demo only (landing page), never silent global AI abuse
    source = (data.get("source") or "").strip().lower()
    if source == "demo" and config.ALLOW_PUBLIC_DEMO:
        biz = db.get_business_by_slug("techflow-electronics")
        if biz:
            return biz, None, None
        return None, "Demo is unavailable", 503

    return None, "widget_key or authenticated business_id required", 400


def _prepare_chat_request(data):
    """Shared validation for /chat and /chat/stream. Returns (ctx, error_response)."""
    if not isinstance(data, dict) or "message" not in data:
        return None, (jsonify({"error": "'message' required"}), 400)

    user_message = security.sanitize_chat_message(data.get("message") or "")
    if not user_message:
        return None, (jsonify({"error": "Message cannot be empty"}), 400)

    session_id = _validate_session_id(
        (data.get("session_id") or "").strip()
    ) or str(uuid.uuid4())
    source = (data.get("source") or "api").strip().lower()
    use_ai = data.get("use_ai", None)

    biz, err, code = _resolve_business_for_chat(data)
    if err:
        return None, (jsonify({"error": err}), code)

    # Rate limits
    if data.get("widget_key") or _widget_key_from_request():
        key = (data.get("widget_key") or _widget_key_from_request()).strip()
        if not security.limiter.allow(
            f"chat-widget:{key}", config.RATE_LIMIT_CHAT_WIDGET, 60.0
        ):
            return None, (jsonify({"error": "Rate limit exceeded"}), 429)
    elif source == "demo":
        limited = _rate_limit_or_429("chat-demo", config.RATE_LIMIT_DEMO)
        if limited:
            return None, limited
    else:
        limited = _rate_limit_or_429("chat", config.RATE_LIMIT_CHAT)
        if limited:
            return None, limited

    # Consume preview credit BEFORE expensive generation (atomic)
    is_widget = bool(data.get("widget_key") or _widget_key_from_request())
    if not is_widget and source != "demo":
        if not db.try_consume_preview_chat(biz["id"], config.FREE_PREVIEW_CHAT_LIMIT):
            return None, (
                jsonify({"error": "Free preview limit reached. Subscribe to continue."}),
                402,
            )

    model = (biz.get("ai_model") or config.DEFAULT_MODEL).strip().lower()
    if model not in ("mistral", "llama3", "neural-chat"):
        model = config.DEFAULT_MODEL

    try:
        db.ensure_session(session_id, business_id=biz["id"])
    except ValueError:
        return None, (jsonify({"error": "Invalid session for this business"}), 403)

    return {
        "user_message": user_message,
        "session_id": session_id,
        "source": source,
        "use_ai": use_ai,
        "biz": biz,
        "model": model,
        "knowledge": biz.get("knowledge") or {},
    }, None


@app.route("/chat", methods=["POST"])
def chat_endpoint():
    try:
        data = request.get_json(silent=True)
        ctx, err = _prepare_chat_request(data if isinstance(data, dict) else {})
        if err:
            return err

        conversation_history = db.get_recent_conversation(ctx["session_id"], limit=4)
        chatbot_response = chat(
            ctx["user_message"],
            use_ai=ctx["use_ai"],
            model=ctx["model"],
            conversation_history=conversation_history,
            business_data=ctx["knowledge"],
        )
        if not isinstance(chatbot_response, dict):
            chatbot_response = {
                "response": str(chatbot_response),
                "intent": "system",
                "confidence": 1.0,
                "model_used": "fallback",
            }

        # Final customer-facing cleanup (belt-and-suspenders)
        bot = get_chatbot(model=ctx["model"], business_data=ctx["knowledge"])
        chatbot_response["response"] = bot._sanitize_customer_reply(
            chatbot_response.get("response") or ""
        )

        timestamp = now_utc()
        chatbot_response["timestamp"] = timestamp
        chatbot_response["session_id"] = ctx["session_id"]
        chatbot_response["business_id"] = ctx["biz"]["id"]
        chatbot_response["business_name"] = ctx["biz"]["name"]

        try:
            db.save_message(
                ctx["session_id"],
                "user",
                ctx["user_message"],
                timestamp=timestamp,
                business_id=ctx["biz"]["id"],
            )
            db.save_message(
                ctx["session_id"],
                "bot",
                chatbot_response["response"],
                intent=chatbot_response.get("intent"),
                confidence=chatbot_response.get("confidence"),
                model_used=chatbot_response.get("model_used"),
                timestamp=timestamp,
                business_id=ctx["biz"]["id"],
            )
        except Exception as e:
            logger.warning(f"Could not save to database: {e}")

        return jsonify(chatbot_response), 200
    except Exception as e:
        return jsonify(
            {
                "error": _client_error_message(e),
                "response": "An error occurred processing your request.",
                "intent": "error",
                "confidence": 0.0,
                "model_used": "system",
                "timestamp": now_utc(),
            }
        ), 500


@app.route("/chat/stream", methods=["POST"])
def chat_stream_endpoint():
    """SSE streaming chat — same auth/tenant rules as /chat, tokens arrive live."""
    data = request.get_json(silent=True)
    ctx, err = _prepare_chat_request(data if isinstance(data, dict) else {})
    if err:
        return err

    conversation_history = db.get_recent_conversation(ctx["session_id"], limit=4)
    biz = ctx["biz"]
    model = ctx["model"]
    user_message = ctx["user_message"]
    session_id = ctx["session_id"]
    knowledge = ctx["knowledge"]
    use_ai = ctx["use_ai"]

    def event_stream():
        full_text = ""
        final_meta = {
            "intent": "ai_generated",
            "confidence": 0.8,
            "model_used": f"ollama_{model}",
        }
        try:
            for event in stream_chat(
                user_message,
                use_ai=use_ai,
                model=model,
                conversation_history=conversation_history,
                business_data=knowledge,
            ):
                etype = event.get("type")
                if etype == "meta":
                    final_meta["intent"] = event.get("intent", final_meta["intent"])
                    final_meta["confidence"] = event.get(
                        "confidence", final_meta["confidence"]
                    )
                    final_meta["model_used"] = event.get(
                        "model_used", final_meta["model_used"]
                    )
                    yield f"data: {json.dumps({'type': 'meta', **final_meta})}\n\n"
                elif etype == "token":
                    piece = event.get("text") or ""
                    full_text += piece
                    yield f"data: {json.dumps({'type': 'token', 'text': piece})}\n\n"
                elif etype == "done":
                    full_text = event.get("response") or full_text
                    final_meta["intent"] = event.get("intent", final_meta["intent"])
                    final_meta["confidence"] = event.get(
                        "confidence", final_meta["confidence"]
                    )
                    final_meta["model_used"] = event.get(
                        "model_used", final_meta["model_used"]
                    )
                    break

            # Final customer-facing cleanup before save / SSE done
            bot = get_chatbot(model=model, business_data=knowledge)
            full_text = bot._sanitize_customer_reply(full_text or "")

            timestamp = now_utc()
            try:
                db.save_message(
                    session_id,
                    "user",
                    user_message,
                    timestamp=timestamp,
                    business_id=biz["id"],
                )
                db.save_message(
                    session_id,
                    "bot",
                    full_text,
                    intent=final_meta.get("intent"),
                    confidence=final_meta.get("confidence"),
                    model_used=final_meta.get("model_used"),
                    timestamp=timestamp,
                    business_id=biz["id"],
                )
            except Exception as e:
                logger.warning(f"Could not save streamed chat: {e}")

            done_payload = {
                "type": "done",
                "response": full_text,
                "session_id": session_id,
                "business_id": biz["id"],
                "business_name": biz["name"],
                "timestamp": timestamp,
                **final_meta,
            }
            yield f"data: {json.dumps(done_payload)}\n\n"
        except Exception as e:
            logger.error(f"Stream chat error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': 'Stream failed'})}\n\n"

    return Response(
        stream_with_context(event_stream()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.route("/models", methods=["GET"])
def get_models():
    try:
        import requests

        response = requests.get(f"{config.OLLAMA_HOST}/api/tags", timeout=2)
        if response.status_code == 200:
            models = [tag["name"] for tag in response.json().get("models", [])]
            return jsonify(
                {
                    "ollama_available": True,
                    "available_models": models,
                    "recommended": "mistral, llama3, neural-chat",
                }
            ), 200
        return jsonify(
            {"ollama_available": False, "message": "Ollama not responding"}
        ), 200
    except Exception:
        return jsonify(
            {
                "ollama_available": False,
                "message": "Ollama not reachable",
                "solution": "Install and start Ollama: https://ollama.ai",
            }
        ), 200


@app.route("/logs", methods=["GET"])
@require_auth
def get_logs():
    business_id = request.args.get("business_id")
    session_id = request.args.get("session_id")
    limit = min(request.args.get("limit", 100, type=int) or 100, 500)

    if session_id and not business_id:
        session_id = _validate_session_id(session_id)
        if not session_id:
            return jsonify({"error": "Invalid session_id"}), 400
        sess = db.get_session(session_id)
        if not sess or not sess.get("business_id"):
            return jsonify({"error": "Forbidden"}), 403
        business_id = sess["business_id"]

    if not business_id:
        return jsonify({"error": "business_id is required"}), 400

    biz = db.get_business_by_id(business_id)
    if not biz or biz["owner_id"] != request.current_user["id"]:
        return jsonify({"error": "Forbidden"}), 403

    if session_id:
        sess = db.get_session(session_id)
        if not sess or sess.get("business_id") != business_id:
            return jsonify({"error": "Forbidden"}), 403

    logs = db.get_logs(
        session_id=session_id, limit=limit, business_id=business_id
    )
    return jsonify({"total": len(logs), "logs": logs}), 200


@app.route("/logs", methods=["DELETE"])
@require_auth
def clear_logs():
    business_id = request.args.get("business_id")
    if business_id:
        biz = db.get_business_by_id(business_id)
        if not biz or biz["owner_id"] != request.current_user["id"]:
            return jsonify({"error": "Forbidden"}), 403
        db.clear_logs(business_id=business_id)
    else:
        for biz in db.get_businesses_for_user(request.current_user["id"]):
            db.clear_logs(business_id=biz["id"])
    return jsonify({"status": "success", "message": "Logs cleared"}), 200


@app.route("/sessions/<session_id>/messages", methods=["GET"])
@require_auth
def get_session_messages(session_id):
    session_id = _validate_session_id(session_id)
    if not session_id:
        return jsonify({"error": "Invalid session_id"}), 400
    sess = db.get_session(session_id)
    if not sess or not sess.get("business_id"):
        return jsonify({"error": "Not found"}), 404
    biz = db.get_business_by_id(sess["business_id"])
    if not biz or biz["owner_id"] != request.current_user["id"]:
        return jsonify({"error": "Forbidden"}), 403
    messages = db.get_session_messages(session_id)
    return jsonify(
        {"session_id": session_id, "total": len(messages), "messages": messages}
    ), 200


@app.route("/stats", methods=["GET"])
@require_auth
def get_stats():
    business_id = request.args.get("business_id")
    if not business_id:
        return jsonify({"error": "business_id is required"}), 400
    biz = db.get_business_by_id(business_id)
    if not biz or biz["owner_id"] != request.current_user["id"]:
        return jsonify({"error": "Forbidden"}), 403
    return jsonify(db.get_stats(business_id=business_id)), 200


@app.route("/business-info", methods=["GET"])
def get_business_info():
    slug = request.args.get("slug", "techflow-electronics")
    if not isinstance(slug, str) or len(slug) > 80 or not all(
        c.isalnum() or c in "-_" for c in slug
    ):
        return jsonify({"error": "Invalid slug"}), 400
    biz = db.get_business_by_slug(slug)
    if not biz:
        return jsonify({"error": "Business info not available"}), 404
    knowledge = biz.get("knowledge") or {}
    info = knowledge.get("business_info") or {}
    # Public marketing fields only
    return jsonify(
        {
            "name": biz.get("name"),
            "website": biz.get("website") or info.get("website") or "",
            "tagline": info.get("tagline") or "",
            "description": (biz.get("description") or info.get("description") or "")[
                :500
            ],
        }
    ), 200


# ── Stripe ─────────────────────────────────────────────────────────────────


def _plan_from_stripe_subscription(sub) -> str | None:
    """Best-effort plan id from a Stripe Subscription object/dict."""
    if not sub:
        return None
    meta = {}
    try:
        meta = sub.get("metadata") if isinstance(sub, dict) else (getattr(sub, "metadata", None) or {})
        meta = dict(meta or {})
    except Exception:
        meta = {}
    plan = (meta.get("plan") or "").strip().lower()
    if plan and config.get_plan(plan):
        return plan

    price_id = None
    try:
        items = sub.get("items") if isinstance(sub, dict) else getattr(sub, "items", None)
        data = []
        if items is not None:
            data = items.get("data") if isinstance(items, dict) else getattr(items, "data", []) or []
        if data:
            first = data[0]
            price = first.get("price") if isinstance(first, dict) else getattr(first, "price", None)
            if isinstance(price, str):
                price_id = price
            elif isinstance(price, dict):
                price_id = price.get("id")
            elif price is not None:
                price_id = getattr(price, "id", None)
    except Exception:
        price_id = None
    return config.plan_id_for_price(price_id)


def _stripe_client():
    if not config.STRIPE_SECRET_KEY:
        return None
    import stripe

    stripe.api_key = config.STRIPE_SECRET_KEY
    return stripe


@app.route("/billing/config", methods=["GET"])
def billing_config():
    plans = []
    for plan in config.SUBSCRIPTION_PLANS:
        plans.append(
            {
                "id": plan["id"],
                "name": plan["name"],
                "price_cad": plan["price_cad"],
                "description": plan["description"],
                "features": plan["features"],
                "available": bool(plan.get("price_id")),
                "max_businesses": plan.get("max_businesses"),
                "max_knowledge_words": plan.get("max_knowledge_words"),
                "chat_colors": bool(plan.get("chat_colors")),
            }
        )
    return jsonify(
        {
            "publishable_key": config.STRIPE_PUBLISHABLE_KEY,
            "price_id_configured": config.any_stripe_price_configured(),
            "stripe_configured": bool(config.STRIPE_SECRET_KEY),
            "free_preview_limit": config.FREE_PREVIEW_CHAT_LIMIT,
            "product_name": config.PRODUCT_NAME,
            "plans": plans,
            "currency": "cad",
        }
    ), 200


@app.route("/billing/checkout", methods=["POST"])
@require_auth
def create_checkout():
    stripe = _stripe_client()
    if not stripe or not config.any_stripe_price_configured():
        return jsonify(
            {
                "error": "Stripe is not configured. Add STRIPE_SECRET_KEY and plan price IDs to .env",
            }
        ), 503

    data = request.get_json(silent=True) or {}
    business_id = data.get("business_id")
    plan_id = (data.get("plan") or data.get("plan_id") or "basic").strip().lower()
    plan = config.get_plan(plan_id)
    if not plan or not plan.get("price_id"):
        return jsonify(
            {
                "error": f"Unknown or unconfigured plan '{plan_id}'. Choose basic, professional, or premium.",
            }
        ), 400

    biz = db.get_business_by_id(business_id)
    if not biz or biz["owner_id"] != request.current_user["id"]:
        return jsonify({"error": "Business not found"}), 404

    try:
        customer_id = biz.get("stripe_customer_id")
        if not customer_id:
            customer = stripe.Customer.create(
                email=request.current_user["email"],
                name=request.current_user["name"],
                metadata={"business_id": biz["id"], "user_id": request.current_user["id"]},
            )
            customer_id = customer.id
            db.update_business(biz["id"], stripe_customer_id=customer_id)

        session = stripe.checkout.Session.create(
            customer=customer_id,
            mode="subscription",
            line_items=[{"price": plan["price_id"], "quantity": 1}],
            success_url=(
                f"{config.FRONTEND_URL}/billing?success=1"
                f"&business_id={biz['id']}"
                f"&session_id={{CHECKOUT_SESSION_ID}}"
            ),
            cancel_url=f"{config.FRONTEND_URL}/billing?canceled=1&business_id={biz['id']}",
            metadata={"business_id": biz["id"], "plan": plan["id"]},
            subscription_data={
                "metadata": {"business_id": biz["id"], "plan": plan["id"]}
            },
        )
        return jsonify(
            {
                "checkout_url": session.url,
                "session_id": session.id,
                "plan": plan["id"],
            }
        ), 200
    except Exception as e:
        return jsonify({"error": _client_error_message(e)}), 500


@app.route("/billing/confirm", methods=["POST"])
@require_auth
def confirm_checkout():
    """Activate subscription immediately after Stripe Checkout redirect (no webhook wait)."""
    stripe = _stripe_client()
    if not stripe:
        return jsonify({"error": "Stripe is not configured"}), 503

    data = request.get_json(silent=True) or {}
    session_id = (data.get("session_id") or "").strip()
    business_id = data.get("business_id")
    if not session_id or not business_id:
        return jsonify({"error": "session_id and business_id are required"}), 400

    biz = db.get_business_by_id(business_id)
    if not biz or biz["owner_id"] != request.current_user["id"]:
        return jsonify({"error": "Business not found"}), 404

    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except Exception as e:
        logger.error(f"Stripe session retrieve error: {e}")
        return jsonify({"error": "Could not verify checkout session"}), 400

    meta_biz = (session.get("metadata") or {}).get("business_id")
    if not meta_biz or meta_biz != business_id:
        return jsonify({"error": "Checkout session does not match this business"}), 400

    customer = session.get("customer")
    if biz.get("stripe_customer_id") and customer and customer != biz["stripe_customer_id"]:
        return jsonify({"error": "Checkout customer does not match this business"}), 400

    status = session.get("status")
    payment_status = session.get("payment_status")
    if status != "complete" or payment_status not in ("paid", "no_payment_required"):
        return jsonify(
            {
                "error": "Checkout not completed yet",
                "status": status,
                "payment_status": payment_status,
            }
        ), 402

    fields = {"subscription_status": "active"}
    if customer:
        fields["stripe_customer_id"] = customer
    if session.get("subscription"):
        fields["stripe_subscription_id"] = session["subscription"]

    plan_from_meta = (session.get("metadata") or {}).get("plan")
    if plan_from_meta and config.get_plan(plan_from_meta):
        fields["plan"] = plan_from_meta
    elif session.get("subscription"):
        try:
            sub = stripe.Subscription.retrieve(
                session["subscription"], expand=["items.data.price"]
            )
            price_id = None
            items = (sub.get("items") or {}).get("data") or []
            if items:
                price = items[0].get("price") or {}
                price_id = price.get("id") if isinstance(price, dict) else None
            mapped_plan = config.plan_id_for_price(price_id) or (sub.get("metadata") or {}).get(
                "plan"
            )
            if mapped_plan and config.get_plan(mapped_plan):
                fields["plan"] = mapped_plan
        except Exception as e:
            logger.warning("Could not resolve plan from subscription: %s", e)

    biz = db.update_business(business_id, **fields)
    return jsonify(
        {
            "business": db.public_business_view(biz),
            "activated": True,
        }
    ), 200


@app.route("/billing/sync", methods=["POST"])
@require_auth
def sync_subscription():
    """Pull latest subscription status from Stripe (fixes missed webhooks)."""
    stripe = _stripe_client()
    if not stripe:
        return jsonify({"error": "Stripe is not configured"}), 503

    data = request.get_json(silent=True) or {}
    business_id = data.get("business_id")
    logger.info("billing/sync requested business_id=%s user=%s", business_id, request.current_user.get("email"))
    biz = db.get_business_by_id(business_id)
    if not biz or biz["owner_id"] != request.current_user["id"]:
        return jsonify({"error": "Business not found"}), 404

    customer_id = (biz.get("stripe_customer_id") or "").strip()
    subscription_id = (biz.get("stripe_subscription_id") or "").strip()
    if not customer_id and not subscription_id:
        # Business marked active without Stripe link (e.g. demo seed) — not an error crash
        return jsonify(
            {
                "error": (
                    "This business has no Stripe customer yet. "
                    "Click Subscribe / Checkout once, then use Refresh."
                ),
                "business": db.public_business_view(biz),
                "synced": False,
                "found": False,
            }
        ), 400

    try:
        chosen = None
        if subscription_id:
            try:
                chosen = stripe.Subscription.retrieve(subscription_id)
            except Exception as e:
                logger.warning("Subscription.retrieve failed: %s", e)
                chosen = None

        if chosen is None and customer_id:
            try:
                subs = stripe.Subscription.list(
                    customer=customer_id, status="all", limit=10
                )
                items = list(getattr(subs, "data", []) or [])
                for sub in items:
                    status = sub["status"] if "status" in sub else getattr(sub, "status", None)
                    if status in ("active", "trialing"):
                        chosen = sub
                        break
                    if chosen is None:
                        chosen = sub
            except Exception as e:
                logger.warning("Subscription.list failed: %s", e)
                err_text = str(e).lower()
                if "no such customer" in err_text or "resource_missing" in err_text:
                    db.update_business(
                        business_id,
                        stripe_customer_id=None,
                        stripe_subscription_id=None,
                        subscription_status="free",
                        plan="free",
                    )
                    return jsonify(
                        {
                            "error": (
                                "Stripe customer was not found (test data may have been reset). "
                                "Complete Checkout again to reconnect."
                            ),
                            "business": db.public_business_view(
                                db.get_business_by_id(business_id)
                            ),
                            "synced": True,
                            "found": False,
                        }
                    ), 400
                raise

        if not chosen:
            biz = db.update_business(
                business_id, subscription_status="free", plan="free"
            )
            return jsonify(
                {
                    "business": db.public_business_view(biz),
                    "synced": True,
                    "found": False,
                }
            ), 200

        status = chosen["status"] if "status" in chosen else chosen.status
        sub_id = chosen["id"] if "id" in chosen else chosen.id
        cust = chosen["customer"] if "customer" in chosen else chosen.customer
        if cust is not None and not isinstance(cust, str):
            cust = getattr(cust, "id", None) or str(cust)
        mapped = (
            status
            if status in ("active", "trialing", "past_due", "canceled")
            else "active"
        )
        fields = {
            "subscription_status": mapped,
            "stripe_subscription_id": sub_id,
        }
        if cust:
            fields["stripe_customer_id"] = cust
        plan = _plan_from_stripe_subscription(chosen)
        if plan:
            fields["plan"] = plan
        elif mapped in ("canceled", "free"):
            fields["plan"] = "free"
        biz = db.update_business(business_id, **fields)
        return jsonify(
            {
                "business": db.public_business_view(biz),
                "synced": True,
                "found": True,
                "stripe_status": status,
            }
        ), 200
    except Exception as e:
        return jsonify({"error": _client_error_message(e)}), 500


@app.route("/billing/portal", methods=["POST"])
@require_auth
def billing_portal():
    stripe = _stripe_client()
    if not stripe:
        return jsonify({"error": "Stripe is not configured"}), 503

    data = request.get_json(silent=True) or {}
    business_id = data.get("business_id")
    biz = db.get_business_by_id(business_id)
    if not biz or biz["owner_id"] != request.current_user["id"]:
        return jsonify({"error": "Business not found"}), 404
    if not biz.get("stripe_customer_id"):
        return jsonify({"error": "No Stripe customer yet — subscribe first"}), 400

    try:
        session = stripe.billing_portal.Session.create(
            customer=biz["stripe_customer_id"],
            return_url=f"{config.FRONTEND_URL}/billing?business_id={biz['id']}",
        )
        return jsonify({"portal_url": session.url}), 200
    except Exception as e:
        return jsonify({"error": _client_error_message(e)}), 500


@app.route("/billing/webhook", methods=["POST"])
def stripe_webhook():
    stripe = _stripe_client()
    if not stripe:
        return jsonify({"error": "Stripe not configured"}), 503

    payload = request.get_data()
    sig = request.headers.get("Stripe-Signature", "")
    try:
        if config.STRIPE_WEBHOOK_SECRET:
            event = stripe.Webhook.construct_event(
                payload, sig, config.STRIPE_WEBHOOK_SECRET
            )
        elif config.ALLOW_INSECURE_WEBHOOK:
            logger.warning("Stripe webhook accepted without signature (ALLOW_INSECURE_WEBHOOK)")
            event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
        else:
            return jsonify(
                {
                    "error": "STRIPE_WEBHOOK_SECRET is required. "
                    "For local CLI only, set ALLOW_INSECURE_WEBHOOK=true."
                }
            ), 503
    except Exception as e:
        logger.warning(f"Webhook signature error: {e}")
        return jsonify({"error": "Invalid webhook signature"}), 400

    etype = event["type"]
    obj = event["data"]["object"]

    try:
        if etype == "checkout.session.completed":
            business_id = (obj.get("metadata") or {}).get("business_id")
            sub_id = obj.get("subscription")
            customer_id = obj.get("customer")
            if business_id:
                fields = {"subscription_status": "active"}
                if sub_id:
                    fields["stripe_subscription_id"] = sub_id
                if customer_id:
                    fields["stripe_customer_id"] = customer_id
                plan = (obj.get("metadata") or {}).get("plan")
                if plan and config.get_plan(plan):
                    fields["plan"] = plan
                db.update_business(business_id, **fields)

        elif etype in (
            "customer.subscription.updated",
            "customer.subscription.created",
        ):
            business_id = (obj.get("metadata") or {}).get("business_id")
            status = obj.get("status")  # active, trialing, past_due, canceled
            if not business_id and obj.get("customer"):
                # Lookup by customer
                with db.get_connection() as conn:
                    row = conn.execute(
                        "SELECT id FROM businesses WHERE stripe_customer_id = ?",
                        (obj["customer"],),
                    ).fetchone()
                    business_id = row["id"] if row else None
            if business_id and status:
                mapped = status if status in (
                    "active",
                    "trialing",
                    "past_due",
                    "canceled",
                ) else "active"
                fields = {
                    "subscription_status": mapped,
                    "stripe_subscription_id": obj.get("id"),
                }
                plan = _plan_from_stripe_subscription(obj)
                if plan:
                    fields["plan"] = plan
                elif mapped == "canceled":
                    fields["plan"] = "free"
                db.update_business(business_id, **fields)

        elif etype == "customer.subscription.deleted":
            business_id = (obj.get("metadata") or {}).get("business_id")
            if not business_id and obj.get("customer"):
                with db.get_connection() as conn:
                    row = conn.execute(
                        "SELECT id FROM businesses WHERE stripe_customer_id = ?",
                        (obj["customer"],),
                    ).fetchone()
                    business_id = row["id"] if row else None
            if business_id:
                db.update_business(
                    business_id, subscription_status="canceled", plan="free"
                )
    except Exception as e:
        logger.error(f"Webhook handler error: {e}")
        return jsonify({"error": "Webhook handler failed"}), 500

    return jsonify({"received": True}), 200


# ── Widget static ──────────────────────────────────────────────────────────


@app.route("/embed/sessions/<session_id>/messages", methods=["GET"])
def embed_session_messages(session_id):
    """
    Public widget history: load messages for a visitor session.
    Requires a valid widget key; session must belong to that business.
    """
    key = (request.args.get("key") or _widget_key_from_request() or "").strip()
    if not key:
        return jsonify({"error": "Widget key required"}), 400
    biz = db.get_business_by_widget_key(key)
    if not biz:
        return jsonify({"error": "Invalid key"}), 404
    if not can_use_embed(biz):
        return jsonify({"error": "Subscription inactive", "active": False}), 402
    origin_err = _enforce_widget_origin(biz)
    if origin_err:
        return jsonify({"error": origin_err[0]}), origin_err[1]

    session_id = _validate_session_id(session_id)
    if not session_id:
        return jsonify({"error": "Invalid session_id"}), 400
    sess = db.get_session(session_id)
    if not sess or sess.get("business_id") != biz["id"]:
        return jsonify({"error": "Not found"}), 404

    limited = _rate_limit_or_429("embed-history", config.RATE_LIMIT_CHAT_WIDGET)
    if limited:
        return limited

    messages = db.get_session_messages(session_id, limit=100)
    # Public payload: no intent/confidence/model internals needed for widget UI
    safe = [
        {
            "role": "bot" if m.get("role") == "bot" else "user",
            "content": m.get("content") or "",
            "timestamp": m.get("timestamp"),
        }
        for m in messages
    ]
    return jsonify(
        {
            "session_id": session_id,
            "total": len(safe),
            "messages": safe,
            "business_name": biz["name"],
        }
    ), 200


@app.route("/widget.js", methods=["GET"])
def widget_js():
    return send_from_directory(STATIC_DIR, "widget.js", mimetype="application/javascript")


@app.route("/embed/config", methods=["GET"])
def embed_config():
    key = request.args.get("key", "")
    biz = db.get_business_by_widget_key(key)
    if not biz:
        return jsonify({"error": "Invalid key"}), 404
    if not can_use_embed(biz):
        return jsonify({"error": "Subscription inactive", "active": False}), 402
    origin_err = _enforce_widget_origin(biz)
    if origin_err:
        return jsonify({"error": origin_err[0], "active": False}), origin_err[1]
    knowledge = biz.get("knowledge") or {}
    info = knowledge.get("business_info") or {}
    view = db.public_business_view(biz)
    return jsonify(
        {
            "active": True,
            "business_name": biz["name"],
            "tagline": info.get("tagline") or "Customer Support",
            "api_base": request.url_root.rstrip("/"),
            "chat_colors": (view or {}).get("chat_colors") or config.DEFAULT_CHAT_COLORS,
            "plan": (view or {}).get("effective_plan") or "free",
        }
    ), 200


# Serve built React SPA for client-side routes (/dashboard, /signup, …)
# Registered last so it never shadows API endpoints.
@app.route("/<path:path>", methods=["GET"])
def spa_fallback(path):
    # Never hijack API-ish paths (GET-only catch-all; POSTs already have their own routes)
    api_prefixes = (
        "auth/",
        "businesses/",
        "billing/",
        "sessions/",
        "embed/",
        "chat/",
        "api/",
    )
    api_exact = {"chat", "stats", "models", "logs", "widget.js", "favicon.ico"}
    if path in api_exact or any(path.startswith(p) for p in api_prefixes):
        return jsonify({"error": "Endpoint not found"}), 404

    file_path = os.path.join(FRONTEND_DIST, path)
    if os.path.isfile(file_path):
        return send_from_directory(FRONTEND_DIST, path)

    index = os.path.join(FRONTEND_DIST, "index.html")
    if os.path.isfile(index):
        return send_from_directory(FRONTEND_DIST, "index.html")

    return jsonify(
        {
            "error": "Frontend not built. Run: cd frontend-react && npm run build",
            "path": path,
        }
    ), 404


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error("Internal error: %s", error)
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    db.init_db()
    os.makedirs(STATIC_DIR, exist_ok=True)

    frontend_ready = os.path.isfile(os.path.join(FRONTEND_DIST, "index.html"))
    public = config.PUBLIC_BASE_URL or config.FRONTEND_URL

    print("=" * 70)
    print(f"{config.PRODUCT_NAME} — SaaS Customer Chatbot")
    print("=" * 70)
    print(f"Environment: {config.ENVIRONMENT}")
    print(f"Server: http://{config.HOST}:{config.PORT}")
    print(f"Frontend URL (Stripe redirects): {config.FRONTEND_URL}")
    print(f"Public base: {public}")
    print(f"Widget: http://{config.HOST}:{config.PORT}/widget.js")
    print(
        "SPA build: "
        + ("ready (serving frontend-react/dist)" if frontend_ready else "MISSING — run npm run build")
    )
    if not config.IS_PRODUCTION:
        print("Demo login: demo@supportflow.local / demo1234")
    print("Ollama: ollama serve  (must stay running on this laptop)")
    if not config.STRIPE_SECRET_KEY:
        print("Stripe: not configured (billing endpoints return 503 until .env set)")
    print("=" * 70)
    print("Laptop share tip: build frontend, set FRONTEND_URL to your tunnel URL,")
    print("then run a tunnel to this port (see HOSTING_LAPTOP.md).")
    print("=" * 70)

    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)

