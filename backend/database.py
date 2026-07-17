"""
SQLite database layer — multi-tenant SaaS (users, businesses, chat logs).
"""

import json
import os
import secrets
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "chat_logs.db")
CHAT_LOGS_JSON = os.path.join(os.path.dirname(__file__), "chat_logs.json")
BUSINESS_DATA_PATH = os.path.join(os.path.dirname(__file__), "business_data.json")


def now_utc():
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _row_to_dict(row):
    if row is None:
        return None
    return dict(row)


def init_db():
    """Create tables and seed TechFlow demo tenant."""
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS businesses (
                id TEXT PRIMARY KEY,
                owner_id TEXT NOT NULL,
                name TEXT NOT NULL,
                slug TEXT NOT NULL UNIQUE,
                website TEXT,
                description TEXT,
                knowledge_json TEXT NOT NULL DEFAULT '{}',
                widget_key TEXT NOT NULL UNIQUE,
                stripe_customer_id TEXT,
                stripe_subscription_id TEXT,
                subscription_status TEXT NOT NULL DEFAULT 'free',
                preview_chat_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (owner_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                business_id TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (business_id) REFERENCES businesses(id)
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                intent TEXT,
                confidence REAL,
                model_used TEXT,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            );

            CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
            CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);
            CREATE INDEX IF NOT EXISTS idx_businesses_owner ON businesses(owner_id);
            CREATE INDEX IF NOT EXISTS idx_businesses_widget ON businesses(widget_key);
            CREATE INDEX IF NOT EXISTS idx_sessions_business ON sessions(business_id);
            """
        )

        # Migrate older sessions table missing business_id
        cols = {
            r["name"]
            for r in conn.execute("PRAGMA table_info(sessions)").fetchall()
        }
        if "business_id" not in cols:
            conn.execute("ALTER TABLE sessions ADD COLUMN business_id TEXT")

        biz_cols = {
            r["name"]
            for r in conn.execute("PRAGMA table_info(businesses)").fetchall()
        }
        if "ai_model" not in biz_cols:
            conn.execute(
                "ALTER TABLE businesses ADD COLUMN ai_model TEXT NOT NULL DEFAULT 'mistral'"
            )
        if "allowed_origins" not in biz_cols:
            conn.execute(
                "ALTER TABLE businesses ADD COLUMN allowed_origins TEXT NOT NULL DEFAULT '[]'"
            )
        if "plan" not in biz_cols:
            conn.execute(
                "ALTER TABLE businesses ADD COLUMN plan TEXT NOT NULL DEFAULT 'free'"
            )
        if "chat_colors" not in biz_cols:
            conn.execute(
                "ALTER TABLE businesses ADD COLUMN chat_colors TEXT NOT NULL DEFAULT '{}'"
            )

    migrate_json_logs()
    seed_techflow_demo()


def generate_widget_key():
    return "pk_" + secrets.token_urlsafe(24)


def _slugify(name):
    slug = "".join(c.lower() if c.isalnum() else "-" for c in name).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "business"


def seed_techflow_demo():
    """Seed TechFlow as a demo business owned by demo@supportflow.local."""
    from werkzeug.security import generate_password_hash

    with get_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM businesses WHERE slug = ?", ("techflow-electronics",)
        ).fetchone()
        if existing:
            return

        knowledge = {}
        if os.path.exists(BUSINESS_DATA_PATH):
            try:
                with open(BUSINESS_DATA_PATH, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                    # Free-text knowledge preferred; keep structured dump for demo seed
                    knowledge = {
                        "text": json.dumps(raw, indent=2),
                        "business_info": raw.get("business_info", {}),
                    }
            except (OSError, json.JSONDecodeError):
                knowledge = {"text": ""}

        demo_email = "demo@supportflow.local"
        user = conn.execute(
            "SELECT id FROM users WHERE email = ?", (demo_email,)
        ).fetchone()
        if not user:
            user_id = str(uuid.uuid4())
            conn.execute(
                """INSERT INTO users (id, email, password_hash, name, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    user_id,
                    demo_email,
                    generate_password_hash("demo1234"),
                    "TechFlow Demo",
                    now_utc(),
                ),
            )
        else:
            user_id = user["id"]

        biz_id = str(uuid.uuid4())
        ts = now_utc()
        info = knowledge.get("business_info", {})
        conn.execute(
            """INSERT INTO businesses
               (id, owner_id, name, slug, website, description, knowledge_json,
                widget_key, subscription_status, preview_chat_count, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active', 0, ?, ?)""",
            (
                biz_id,
                user_id,
                info.get("name", "TechFlow Electronics"),
                "techflow-electronics",
                info.get("website", "www.techflowelectronics.com"),
                info.get("description", ""),
                json.dumps(knowledge),
                generate_widget_key(),
                ts,
                ts,
            ),
        )


# ── Users ──────────────────────────────────────────────────────────────────


def create_user(email, password_hash, name):
    user_id = str(uuid.uuid4())
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO users (id, email, password_hash, name, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, email.lower().strip(), password_hash, name.strip(), now_utc()),
        )
    return get_user_by_id(user_id)


def get_user_by_email(email):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email.lower().strip(),)
        ).fetchone()
    return _row_to_dict(row)


def get_user_by_id(user_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    return _row_to_dict(row)


# ── Businesses ─────────────────────────────────────────────────────────────


def create_business(owner_id, name, website="", description=""):
    biz_id = str(uuid.uuid4())
    base_slug = _slugify(name)
    slug = base_slug
    ts = now_utc()
    starter = (
        f"Company name: {name.strip()}\n"
        f"Website: {website.strip()}\n"
        f"About: {description.strip()}\n\n"
        "Add your products, shipping policy, returns, support hours, FAQs, "
        "and any other customer-support information below.\n"
    )
    knowledge = {
        "text": starter,
        "business_info": {
            "name": name,
            "website": website,
            "description": description,
        },
    }
    with get_connection() as conn:
        n = 1
        while conn.execute(
            "SELECT id FROM businesses WHERE slug = ?", (slug,)
        ).fetchone():
            slug = f"{base_slug}-{n}"
            n += 1
        conn.execute(
            """INSERT INTO businesses
               (id, owner_id, name, slug, website, description, knowledge_json,
                widget_key, subscription_status, preview_chat_count, created_at, updated_at, ai_model)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'free', 0, ?, ?, 'mistral')""",
            (
                biz_id,
                owner_id,
                name.strip(),
                slug,
                website.strip(),
                description.strip(),
                json.dumps(knowledge),
                generate_widget_key(),
                ts,
                ts,
            ),
        )
    return get_business_by_id(biz_id)


def get_business_by_id(business_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM businesses WHERE id = ?", (business_id,)
        ).fetchone()
    return _business_dict(row)


def get_business_by_slug(slug):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM businesses WHERE slug = ?", (slug,)
        ).fetchone()
    return _business_dict(row)


def get_business_by_widget_key(widget_key):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM businesses WHERE widget_key = ?", (widget_key,)
        ).fetchone()
    return _business_dict(row)


def get_businesses_for_user(owner_id):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM businesses WHERE owner_id = ? ORDER BY created_at DESC",
            (owner_id,),
        ).fetchall()
    return [_business_dict(r) for r in rows]


def _business_dict(row):
    if row is None:
        return None
    d = dict(row)
    try:
        d["knowledge"] = json.loads(d.pop("knowledge_json") or "{}")
    except json.JSONDecodeError:
        d["knowledge"] = {}
    try:
        origins = d.get("allowed_origins") or "[]"
        if isinstance(origins, str):
            d["allowed_origins"] = json.loads(origins)
        if not isinstance(d.get("allowed_origins"), list):
            d["allowed_origins"] = []
    except json.JSONDecodeError:
        d["allowed_origins"] = []
    try:
        colors = d.get("chat_colors") or "{}"
        if isinstance(colors, str):
            d["chat_colors"] = json.loads(colors)
        if not isinstance(d.get("chat_colors"), dict):
            d["chat_colors"] = {}
    except (json.JSONDecodeError, TypeError):
        d["chat_colors"] = {}
    return d


def update_business(business_id, **fields):
    allowed = {
        "name",
        "website",
        "description",
        "knowledge",
        "stripe_customer_id",
        "stripe_subscription_id",
        "subscription_status",
        "preview_chat_count",
        "widget_key",
        "ai_model",
        "allowed_origins",
        "plan",
        "chat_colors",
    }
    updates = []
    values = []
    for key, value in fields.items():
        if key not in allowed:
            continue
        col = "knowledge_json" if key == "knowledge" else key
        if key == "knowledge":
            value = json.dumps(value)
        if key == "allowed_origins":
            value = json.dumps(value if isinstance(value, list) else [])
        if key == "chat_colors":
            value = json.dumps(value if isinstance(value, dict) else {})
        updates.append(f"{col} = ?")
        values.append(value)
    if not updates:
        return get_business_by_id(business_id)
    updates.append("updated_at = ?")
    values.append(now_utc())
    values.append(business_id)
    with get_connection() as conn:
        conn.execute(
            f"UPDATE businesses SET {', '.join(updates)} WHERE id = ?",
            values,
        )
    return get_business_by_id(business_id)


def increment_preview_chat_count(business_id):
    with get_connection() as conn:
        conn.execute(
            """UPDATE businesses
               SET preview_chat_count = preview_chat_count + 1, updated_at = ?
               WHERE id = ?""",
            (now_utc(), business_id),
        )
    return get_business_by_id(business_id)


def try_consume_preview_chat(business_id, limit):
    """
    Atomically consume one free preview credit.
    Returns True if allowed (paid tier or credit consumed under limit).
    """
    biz = get_business_by_id(business_id)
    if not biz:
        return False
    status = biz.get("subscription_status") or "free"
    if status in ("active", "trialing"):
        return True
    with get_connection() as conn:
        cur = conn.execute(
            """UPDATE businesses
               SET preview_chat_count = preview_chat_count + 1, updated_at = ?
               WHERE id = ? AND preview_chat_count < ?""",
            (now_utc(), business_id, limit),
        )
        return cur.rowcount > 0


def regenerate_widget_key(business_id):
    key = generate_widget_key()
    return update_business(business_id, widget_key=key)


def public_business_view(biz):
    """Safe fields for API responses (no owner secrets beyond widget key for owner)."""
    if not biz:
        return None
    origins = biz.get("allowed_origins") or []
    if not isinstance(origins, list):
        origins = []
    colors = biz.get("chat_colors") or {}
    if not isinstance(colors, dict):
        colors = {}
    plan = biz.get("plan") or "free"
    status = biz.get("subscription_status") or "free"
    effective = None
    try:
        import config as _cfg

        effective = _cfg.effective_plan_id(plan, status)
        limits = _cfg.plan_limits(effective)
        # Only expose custom colors when Premium is active
        if limits.get("chat_colors"):
            merged = {**_cfg.DEFAULT_CHAT_COLORS, **{
                k: v for k, v in colors.items() if isinstance(v, str) and v.strip()
            }}
        else:
            merged = dict(_cfg.DEFAULT_CHAT_COLORS)
    except Exception:
        effective = "free"
        limits = {"max_businesses": 1, "max_knowledge_words": 200, "chat_colors": False}
        merged = {
            "primary": "#0d6efd",
            "header": "#0b1f33",
            "user_bubble": "#0d6efd",
            "accent": "#2dd4bf",
        }
    return {
        "id": biz["id"],
        "name": biz["name"],
        "slug": biz["slug"],
        "website": biz.get("website") or "",
        "description": biz.get("description") or "",
        "subscription_status": status,
        "plan": plan,
        "effective_plan": effective,
        "plan_limits": limits,
        "preview_chat_count": biz.get("preview_chat_count") or 0,
        "widget_key": biz.get("widget_key"),
        "ai_model": biz.get("ai_model") or "mistral",
        "allowed_origins": origins,
        "chat_colors": merged,
        "knowledge": biz.get("knowledge") or {},
        "knowledge_text": _knowledge_text(biz.get("knowledge") or {}),
        "created_at": biz.get("created_at"),
        "updated_at": biz.get("updated_at"),
        "stripe_customer_id": biz.get("stripe_customer_id"),
    }


def _knowledge_text(knowledge):
    if not isinstance(knowledge, dict):
        return str(knowledge or "")
    text = knowledge.get("text")
    if isinstance(text, str) and text.strip():
        return text
    # Legacy structured knowledge → readable blob
    try:
        return json.dumps(knowledge, indent=2)
    except (TypeError, ValueError):
        return ""


# ── Sessions / messages ────────────────────────────────────────────────────


def get_session(session_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, business_id, created_at FROM sessions WHERE id = ?",
            (session_id,),
        ).fetchone()
    return _row_to_dict(row)


def list_sessions_for_business(business_id, limit=40):
    """Recent chat sessions with preview snippet for history UI."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                s.id AS session_id,
                s.created_at,
                COUNT(m.id) AS message_count,
                MAX(m.timestamp) AS last_activity,
                (
                    SELECT m2.content FROM messages m2
                    WHERE m2.session_id = s.id AND m2.role = 'user'
                    ORDER BY m2.timestamp ASC LIMIT 1
                ) AS preview
            FROM sessions s
            LEFT JOIN messages m ON m.session_id = s.id
            WHERE s.business_id = ?
            GROUP BY s.id
            HAVING COUNT(m.id) > 0
            ORDER BY COALESCE(MAX(m.timestamp), s.created_at) DESC
            LIMIT ?
            """,
            (business_id, limit),
        ).fetchall()
    result = []
    for row in rows:
        d = dict(row)
        preview = (d.get("preview") or "").strip().replace("\n", " ")
        if len(preview) > 80:
            preview = preview[:77] + "…"
        d["preview"] = preview or "Conversation"
        result.append(d)
    return result


def delete_session(session_id, business_id=None):
    """Delete one session and its messages. Returns True if deleted."""
    sess = get_session(session_id)
    if not sess:
        return False
    if business_id and sess.get("business_id") != business_id:
        return False
    with get_connection() as conn:
        conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
    return True


def ensure_session(session_id, business_id=None):
    """Create or bind session. Raises ValueError if session is tied to another tenant."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, business_id FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if not row:
            conn.execute(
                "INSERT INTO sessions (id, business_id, created_at) VALUES (?, ?, ?)",
                (session_id, business_id, now_utc()),
            )
            return
        existing = row["business_id"]
        if business_id and existing and existing != business_id:
            raise ValueError("Session belongs to another business")
        if business_id and not existing:
            conn.execute(
                "UPDATE sessions SET business_id = ? WHERE id = ?",
                (business_id, session_id),
            )


def save_message(
    session_id,
    role,
    content,
    intent=None,
    confidence=None,
    model_used=None,
    timestamp=None,
    business_id=None,
):
    ensure_session(session_id, business_id=business_id)
    ts = timestamp or now_utc()
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO messages
               (session_id, role, content, intent, confidence, model_used, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (session_id, role, content, intent, confidence, model_used, ts),
        )


def get_session_messages(session_id, limit=100):
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT session_id, role, content, intent, confidence,
                      model_used, timestamp
               FROM messages
               WHERE session_id = ?
               ORDER BY timestamp ASC
               LIMIT ?""",
            (session_id, limit),
        ).fetchall()
    return [dict(row) for row in rows]


def get_recent_conversation(session_id, limit=6):
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT role, content FROM messages
               WHERE session_id = ?
               ORDER BY timestamp DESC
               LIMIT ?""",
            (session_id, limit),
        ).fetchall()
    return [dict(row) for row in reversed(rows)]


def get_logs(session_id=None, limit=100, business_id=None):
    with get_connection() as conn:
        if session_id:
            rows = conn.execute(
                """SELECT * FROM messages
                   WHERE session_id = ?
                   ORDER BY timestamp ASC
                   LIMIT ?""",
                (session_id, limit * 2),
            ).fetchall()
        elif business_id:
            rows = conn.execute(
                """SELECT m.* FROM messages m
                   JOIN sessions s ON s.id = m.session_id
                   WHERE s.business_id = ?
                   ORDER BY m.timestamp DESC
                   LIMIT ?""",
                (business_id, limit * 2),
            ).fetchall()
            rows = list(reversed(rows))
        else:
            rows = conn.execute(
                """SELECT * FROM messages
                   ORDER BY timestamp DESC
                   LIMIT ?""",
                (limit * 2,),
            ).fetchall()
            rows = list(reversed(rows))

    logs = []
    pending_user = None
    for row in rows:
        msg = dict(row)
        if msg["role"] == "user":
            pending_user = msg
        elif msg["role"] == "bot" and pending_user:
            logs.append(
                {
                    "user": pending_user["content"],
                    "bot": msg["content"],
                    "intent": msg["intent"] or "unknown",
                    "confidence": msg["confidence"] or 0.0,
                    "model_used": msg["model_used"] or "unknown",
                    "timestamp": msg["timestamp"],
                    "session_id": msg["session_id"],
                }
            )
            pending_user = None

    if session_id is None:
        logs.reverse()
    return logs[-limit:] if len(logs) > limit else logs


def get_stats(business_id=None):
    with get_connection() as conn:
        if business_id:
            bot_rows = conn.execute(
                """SELECT m.intent, m.confidence, m.model_used
                   FROM messages m
                   JOIN sessions s ON s.id = m.session_id
                   WHERE m.role = 'bot' AND s.business_id = ?""",
                (business_id,),
            ).fetchall()
            total_sessions = conn.execute(
                "SELECT COUNT(*) as cnt FROM sessions WHERE business_id = ?",
                (business_id,),
            ).fetchone()["cnt"]
        else:
            bot_rows = conn.execute(
                """SELECT intent, confidence, model_used
                   FROM messages WHERE role = 'bot'"""
            ).fetchall()
            total_sessions = conn.execute(
                "SELECT COUNT(*) as cnt FROM sessions"
            ).fetchone()["cnt"]

    intent_counts = {}
    model_usage = {}
    confidences = []
    fallback_count = 0

    for row in bot_rows:
        intent = row["intent"] or "unknown"
        intent_counts[intent] = intent_counts.get(intent, 0) + 1
        model = row["model_used"] or "unknown"
        model_usage[model] = model_usage.get(model, 0) + 1
        if row["confidence"] and row["confidence"] > 0:
            confidences.append(row["confidence"])
        if intent in ("fallback", "guardrail_block"):
            fallback_count += 1

    total_bot = len(bot_rows)
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    fallback_rate = round(fallback_count / total_bot, 2) if total_bot else 0

    return {
        "total_messages": total_bot,
        "total_sessions": total_sessions,
        "average_confidence": round(avg_confidence, 2),
        "intent_distribution": intent_counts,
        "model_usage": model_usage,
        "fallback_rate": fallback_rate,
    }


def clear_logs(business_id=None):
    with get_connection() as conn:
        if business_id:
            conn.execute(
                """DELETE FROM messages WHERE session_id IN
                   (SELECT id FROM sessions WHERE business_id = ?)""",
                (business_id,),
            )
            conn.execute(
                "DELETE FROM sessions WHERE business_id = ?", (business_id,)
            )
        else:
            conn.execute("DELETE FROM messages")
            conn.execute("DELETE FROM sessions")


def migrate_json_logs():
    if not os.path.exists(CHAT_LOGS_JSON):
        return
    with get_connection() as conn:
        count = conn.execute(
            "SELECT COUNT(*) as cnt FROM messages"
        ).fetchone()["cnt"]
        if count > 0:
            return
    try:
        with open(CHAT_LOGS_JSON, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except (json.JSONDecodeError, OSError):
        return
    if not logs:
        return
    session_id = str(uuid.uuid4())
    ensure_session(session_id)
    for entry in logs:
        ts = entry.get("timestamp", now_utc())
        save_message(session_id, "user", entry.get("user", ""), timestamp=ts)
        save_message(
            session_id,
            "bot",
            entry.get("bot", ""),
            intent=entry.get("intent"),
            confidence=entry.get("confidence"),
            model_used=entry.get("model_used"),
            timestamp=ts,
        )
