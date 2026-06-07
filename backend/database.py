"""
SQLite database layer for chat logs and session tracking.
"""

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), 'chat_logs.db')
CHAT_LOGS_JSON = os.path.join(os.path.dirname(__file__), 'chat_logs.json')


def now_utc():
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    """Create tables and indexes if they do not exist."""
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL
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

            CREATE INDEX IF NOT EXISTS idx_messages_session_id
                ON messages(session_id);
            CREATE INDEX IF NOT EXISTS idx_messages_timestamp
                ON messages(timestamp);
        """)
    migrate_json_logs()


def ensure_session(session_id):
    """Create session row if it does not exist."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id FROM sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if not row:
            conn.execute(
                "INSERT INTO sessions (id, created_at) VALUES (?, ?)",
                (session_id, now_utc()),
            )


def save_message(session_id, role, content, intent=None, confidence=None,
                 model_used=None, timestamp=None):
    """Save a single message (user or bot) to the database."""
    ensure_session(session_id)
    ts = timestamp or now_utc()
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO messages
               (session_id, role, content, intent, confidence, model_used, timestamp)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (session_id, role, content, intent, confidence, model_used, ts),
        )


def get_session_messages(session_id, limit=100):
    """Return messages for a session ordered by timestamp."""
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
    """Return last N messages for multi-turn context."""
    with get_connection() as conn:
        rows = conn.execute(
            """SELECT role, content FROM messages
               WHERE session_id = ?
               ORDER BY timestamp DESC
               LIMIT ?""",
            (session_id, limit),
        ).fetchall()
    messages = [dict(row) for row in reversed(rows)]
    return messages


def get_logs(session_id=None, limit=100):
    """
    Return logs in legacy-compatible format for /logs endpoint.
    Each entry pairs user message with bot response when possible.
    """
    with get_connection() as conn:
        if session_id:
            rows = conn.execute(
                """SELECT * FROM messages
                   WHERE session_id = ?
                   ORDER BY timestamp ASC
                   LIMIT ?""",
                (session_id, limit * 2),
            ).fetchall()
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
        if msg['role'] == 'user':
            pending_user = msg
        elif msg['role'] == 'bot' and pending_user:
            logs.append({
                'user': pending_user['content'],
                'bot': msg['content'],
                'intent': msg['intent'] or 'unknown',
                'confidence': msg['confidence'] or 0.0,
                'model_used': msg['model_used'] or 'unknown',
                'timestamp': msg['timestamp'],
                'session_id': msg['session_id'],
            })
            pending_user = None

    if session_id is None:
        logs.reverse()
    return logs[-limit:] if len(logs) > limit else logs


def get_stats():
    """Return analytics from bot messages."""
    with get_connection() as conn:
        bot_rows = conn.execute(
            """SELECT intent, confidence, model_used
               FROM messages WHERE role = 'bot'"""
        ).fetchall()

        total_sessions = conn.execute(
            "SELECT COUNT(*) as cnt FROM sessions"
        ).fetchone()['cnt']

    intent_counts = {}
    model_usage = {}
    confidences = []
    fallback_count = 0

    for row in bot_rows:
        intent = row['intent'] or 'unknown'
        intent_counts[intent] = intent_counts.get(intent, 0) + 1

        model = row['model_used'] or 'unknown'
        model_usage[model] = model_usage.get(model, 0) + 1

        if row['confidence'] and row['confidence'] > 0:
            confidences.append(row['confidence'])

        if intent == 'fallback':
            fallback_count += 1

    total_bot = len(bot_rows)
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0
    fallback_rate = round(fallback_count / total_bot, 2) if total_bot else 0

    return {
        'total_messages': total_bot,
        'total_sessions': total_sessions,
        'average_confidence': round(avg_confidence, 2),
        'intent_distribution': intent_counts,
        'model_usage': model_usage,
        'fallback_rate': fallback_rate,
    }


def clear_logs():
    """Delete all messages and sessions."""
    with get_connection() as conn:
        conn.execute("DELETE FROM messages")
        conn.execute("DELETE FROM sessions")


def migrate_json_logs():
    """One-time import from chat_logs.json if DB is empty."""
    if not os.path.exists(CHAT_LOGS_JSON):
        return

    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) as cnt FROM messages").fetchone()['cnt']
        if count > 0:
            return

    try:
        with open(CHAT_LOGS_JSON, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    except (json.JSONDecodeError, OSError):
        return

    if not logs:
        return

    import uuid
    session_id = str(uuid.uuid4())
    ensure_session(session_id)

    for entry in logs:
        ts = entry.get('timestamp', now_utc())
        save_message(
            session_id, 'user', entry.get('user', ''),
            timestamp=ts,
        )
        save_message(
            session_id, 'bot', entry.get('bot', ''),
            intent=entry.get('intent'),
            confidence=entry.get('confidence'),
            model_used=entry.get('model_used'),
            timestamp=ts,
        )
