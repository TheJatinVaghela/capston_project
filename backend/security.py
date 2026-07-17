"""
Security helpers: rate limiting, input sanitization, origin checks, password policy.
"""

from __future__ import annotations

import re
import threading
import time
from collections import defaultdict
from typing import Optional
from urllib.parse import urlparse

# ── Limits ─────────────────────────────────────────────────────────────────

MAX_CHAT_MESSAGE_CHARS = 4000
MAX_KNOWLEDGE_CHARS = 80_000
MAX_SESSION_ID_CHARS = 80
MIN_PASSWORD_LENGTH = 10

# Patterns that look like prompt-injection / secrets in knowledge (warn/flag)
INJECTION_HINTS = re.compile(
    r"(?is)("
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions"
    r"|disregard\s+(all\s+)?(previous|prior|above)"
    r"|you\s+are\s+now\s+"
    r"|new\s+system\s+prompt"
    r"|reveal\s+(your\s+)?(system\s+)?prompt"
    r"|jailbreak"
    r")"
)

SECRET_LIKE = re.compile(
    r"(?i)("
    r"\bsk_live_[a-zA-Z0-9]{20,}"
    r"|\bsk_test_[a-zA-Z0-9]{20,}"
    r"|\bAKIA[0-9A-Z]{16}"
    r"|\bghp_[a-zA-Z0-9]{30,}"
    r"|\b-----BEGIN (RSA )?PRIVATE KEY-----"
    r")"
)

CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
HTML_TAGS = re.compile(r"<[^>]+>")


def sanitize_text(text: str, max_chars: int) -> str:
    if not isinstance(text, str):
        text = str(text or "")
    text = text.replace("\x00", "")
    text = CONTROL_CHARS.sub("", text)
    if len(text) > max_chars:
        text = text[:max_chars]
    return text


def sanitize_chat_message(text: str) -> str:
    return sanitize_text((text or "").strip(), MAX_CHAT_MESSAGE_CHARS)


def sanitize_knowledge_text(text: str) -> str:
    return sanitize_text(text or "", MAX_KNOWLEDGE_CHARS)


def strip_html(text: str) -> str:
    return HTML_TAGS.sub("", text or "")


def knowledge_security_warnings(text: str) -> list[str]:
    warnings = []
    if INJECTION_HINTS.search(text or ""):
        warnings.append(
            "Knowledge contains phrases that look like prompt-injection attempts. "
            "They will be treated as data only, never as system instructions."
        )
    if SECRET_LIKE.search(text or ""):
        warnings.append(
            "Knowledge may contain secret-like strings (API keys). Remove them "
            "before saving — they can leak to customers via answers."
        )
    return warnings


def validate_password(password: str) -> Optional[str]:
    if not password or len(password) < MIN_PASSWORD_LENGTH:
        return f"Password must be at least {MIN_PASSWORD_LENGTH} characters"
    if not re.search(r"[A-Za-z]", password):
        return "Password must include at least one letter"
    if not re.search(r"\d", password):
        return "Password must include at least one number"
    return None


def normalize_origin(origin: str) -> str:
    origin = (origin or "").strip().rstrip("/")
    return origin


def origin_host(origin: str) -> str:
    try:
        parsed = urlparse(origin)
        return (parsed.hostname or "").lower()
    except Exception:
        return ""


def parse_allowed_origins(raw) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, list):
        return [normalize_origin(o) for o in raw if o]
    if isinstance(raw, str):
        raw = raw.strip()
        if not raw:
            return []
        if raw.startswith("["):
            import json

            try:
                data = json.loads(raw)
                if isinstance(data, list):
                    return [normalize_origin(o) for o in data if o]
            except json.JSONDecodeError:
                pass
        return [normalize_origin(p) for p in raw.split(",") if p.strip()]
    return []


def origin_allowed(origin: str, allowed: list[str], *, strict: bool) -> bool:
    """
    If allowed list is non-empty, origin must match exactly.
    If empty: allow when not strict (dev); deny cross-check fails in strict mode.
    """
    origin = normalize_origin(origin)
    if not origin:
        # Non-browser clients (curl, native) — allowed; rate limits still apply
        return True
    allowed = [normalize_origin(a) for a in (allowed or []) if a]
    if allowed:
        return origin in allowed
    return not strict


class RateLimiter:
    """Simple in-process sliding-window rate limiter."""

    def __init__(self):
        self._lock = threading.Lock()
        self._hits: dict[str, list[float]] = defaultdict(list)

    def allow(self, key: str, limit: int, window_sec: float) -> bool:
        now = time.time()
        with self._lock:
            bucket = self._hits[key]
            cutoff = now - window_sec
            # Drop expired
            i = 0
            for t in bucket:
                if t >= cutoff:
                    break
                i += 1
            if i:
                del bucket[:i]
            if len(bucket) >= limit:
                return False
            bucket.append(now)
            return True


limiter = RateLimiter()


def client_ip(request) -> str:
    forwarded = (request.headers.get("X-Forwarded-For") or "").split(",")[0].strip()
    if forwarded:
        return forwarded
    return request.remote_addr or "unknown"
