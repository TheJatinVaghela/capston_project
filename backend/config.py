"""Application configuration from environment variables."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
# override=True so values in backend/.env win over empty shell env vars
load_dotenv(BASE_DIR / ".env", override=True)
load_dotenv(BASE_DIR.parent / ".env", override=False)

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").strip().lower()
IS_PRODUCTION = ENVIRONMENT == "production"

_DEFAULT_SECRET = "supportflow-dev-secret-change-me"
SECRET_KEY = os.getenv("SECRET_KEY", _DEFAULT_SECRET)
JWT_EXPIRY_HOURS = int(os.getenv("JWT_EXPIRY_HOURS", "24"))

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "mistral")

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
# Legacy single-price env (maps to Basic if plan-specific IDs are unset)
STRIPE_PRICE_ID = os.getenv("STRIPE_PRICE_ID", "")
STRIPE_PRICE_ID_BASIC = os.getenv("STRIPE_PRICE_ID_BASIC", "") or STRIPE_PRICE_ID
STRIPE_PRICE_ID_PROFESSIONAL = os.getenv("STRIPE_PRICE_ID_PROFESSIONAL", "")
STRIPE_PRICE_ID_PREMIUM = os.getenv("STRIPE_PRICE_ID_PREMIUM", "")

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")
FREE_PREVIEW_CHAT_LIMIT = int(os.getenv("FREE_PREVIEW_CHAT_LIMIT", "100"))

PRODUCT_NAME = os.getenv("PRODUCT_NAME", "SupportFlow")

# Catalog of monthly subscription plans (Stripe Price IDs from Dashboard)
# Limits: max businesses (account-wide, highest active plan wins),
# knowledge word cap (per business plan), chat color customization (Premium only).
PLAN_LIMITS = {
    "free": {
        "max_businesses": 1,
        "max_knowledge_words": 200,
        "chat_colors": False,
    },
    "basic": {
        "max_businesses": 1,
        "max_knowledge_words": 500,
        "chat_colors": False,
    },
    "professional": {
        "max_businesses": 5,
        "max_knowledge_words": 2000,
        "chat_colors": False,
    },
    "premium": {
        "max_businesses": 10,
        "max_knowledge_words": 5000,
        "chat_colors": True,
    },
}

PLAN_RANK = {"free": 0, "basic": 1, "professional": 2, "premium": 3}

DEFAULT_CHAT_COLORS = {
    "primary": "#0d6efd",
    "header": "#0b1f33",
    "user_bubble": "#0d6efd",
    "accent": "#2dd4bf",
}

SUBSCRIPTION_PLANS = [
    {
        "id": "basic",
        "name": "Basic",
        "price_cad": 5,
        "price_id": STRIPE_PRICE_ID_BASIC,
        "description": "Embed widget + AI model settings for one business.",
        "features": [
            "1 business",
            "500-word knowledge base",
            "Website embed widget",
            "Choose AI model",
        ],
        **PLAN_LIMITS["basic"],
    },
    {
        "id": "professional",
        "name": "Professional",
        "price_cad": 10,
        "price_id": STRIPE_PRICE_ID_PROFESSIONAL,
        "description": "For growing support volume on your store.",
        "features": [
            "Up to 5 businesses",
            "2,000-word knowledge base",
            "Everything in Basic",
        ],
        **PLAN_LIMITS["professional"],
    },
    {
        "id": "premium",
        "name": "Premium",
        "price_cad": 20,
        "price_id": STRIPE_PRICE_ID_PREMIUM,
        "description": "Highest tier for busy customer-support teams.",
        "features": [
            "Up to 10 businesses",
            "5,000-word knowledge base",
            "Custom chatbot colors",
            "Everything in Professional",
        ],
        **PLAN_LIMITS["premium"],
    },
]


def get_plan(plan_id: str):
    """Return a plan dict by id, or None."""
    plan_id = (plan_id or "").strip().lower()
    for plan in SUBSCRIPTION_PLANS:
        if plan["id"] == plan_id:
            return plan
    return None


def plan_id_for_price(price_id: str):
    """Map a Stripe price id back to our plan id."""
    price_id = (price_id or "").strip()
    if not price_id:
        return None
    for plan in SUBSCRIPTION_PLANS:
        if plan.get("price_id") and plan["price_id"] == price_id:
            return plan["id"]
    return None


def any_stripe_price_configured() -> bool:
    return any(p.get("price_id") for p in SUBSCRIPTION_PLANS)


def effective_plan_id(plan_id: str, subscription_status: str = "free") -> str:
    """Paid plan only counts when subscription is active/trialing."""
    status = (subscription_status or "free").strip().lower()
    pid = (plan_id or "free").strip().lower()
    if status not in ("active", "trialing"):
        return "free"
    if pid not in PLAN_LIMITS:
        return "free"
    return pid


def plan_limits(plan_id: str) -> dict:
    pid = (plan_id or "free").strip().lower()
    return dict(PLAN_LIMITS.get(pid) or PLAN_LIMITS["free"])


def highest_account_plan(businesses) -> str:
    """Best active plan across a user's businesses (drives business-count limit)."""
    best = "free"
    best_rank = 0
    for biz in businesses or []:
        pid = effective_plan_id(biz.get("plan"), biz.get("subscription_status"))
        rank = PLAN_RANK.get(pid, 0)
        if rank > best_rank:
            best = pid
            best_rank = rank
    return best


def count_words(text: str) -> int:
    import re

    return len(re.findall(r"\S+", text or ""))

# Local Flask debug (never enable in production)
DEBUG = os.getenv("FLASK_DEBUG", "0").strip() in ("1", "true", "True", "yes")
if IS_PRODUCTION:
    DEBUG = False

# Public landing demo chat (TechFlow). Disable in production.
ALLOW_PUBLIC_DEMO = os.getenv(
    "ALLOW_PUBLIC_DEMO", "false" if IS_PRODUCTION else "true"
).strip().lower() in ("1", "true", "yes")

# When true, widget requests from a browser Origin must match business allowlist.
# Empty allowlist rejects cross-origin widget traffic in production.
WIDGET_STRICT_ORIGINS = os.getenv(
    "WIDGET_STRICT_ORIGINS", "true" if IS_PRODUCTION else "false"
).strip().lower() in ("1", "true", "yes")

# Allow unsigned Stripe webhooks only for local CLI testing (never production)
ALLOW_INSECURE_WEBHOOK = os.getenv("ALLOW_INSECURE_WEBHOOK", "false").strip().lower() in (
    "1",
    "true",
    "yes",
)
if IS_PRODUCTION:
    ALLOW_INSECURE_WEBHOOK = False

ALLOW_INSECURE_DEFAULTS = os.getenv("ALLOW_INSECURE_DEFAULTS", "false").strip().lower() in (
    "1",
    "true",
    "yes",
)

# Rate limits (per IP unless noted)
RATE_LIMIT_AUTH = int(os.getenv("RATE_LIMIT_AUTH", "20"))  # /minute
RATE_LIMIT_CHAT = int(os.getenv("RATE_LIMIT_CHAT", "40"))  # /minute
RATE_LIMIT_CHAT_WIDGET = int(os.getenv("RATE_LIMIT_CHAT_WIDGET", "60"))  # /minute per key
RATE_LIMIT_DEMO = int(os.getenv("RATE_LIMIT_DEMO", "20"))  # /minute


def validate_security_config():
    """Fail fast on unsafe production / secret configuration."""
    problems = []
    insecure_secret = (
        not SECRET_KEY
        or SECRET_KEY == _DEFAULT_SECRET
        or SECRET_KEY in (
            "change-me-to-a-long-random-string",
            "supportflow-jwt-dev-secret-change-in-production",
        )
        or len(SECRET_KEY) < 32
    )
    if insecure_secret:
        if IS_PRODUCTION:
            problems.append(
                "SECRET_KEY must be a strong random string (>= 32 chars). "
                "Set SECRET_KEY in backend/.env before production deploy."
            )
        else:
            print(
                "WARNING: Weak/default SECRET_KEY — OK for local only. "
                "Use a strong SECRET_KEY (>= 32 chars) before any real deploy.",
                file=sys.stderr,
            )

    if IS_PRODUCTION and not STRIPE_WEBHOOK_SECRET and STRIPE_SECRET_KEY:
        problems.append(
            "STRIPE_WEBHOOK_SECRET is required in production when Stripe is configured."
        )

    if problems:
        for p in problems:
            print(f"CONFIG ERROR: {p}", file=sys.stderr)
        sys.exit(1)
