from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

DB_PATH = Path(__file__).parent / "data" / "biblegpt.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_message TEXT NOT NULL,
                assistant_message TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS saved_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                note TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(chat_id) REFERENCES chats(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            """
        )


def add_chat(user_message: str, assistant_message: str) -> int:
    now = datetime.utcnow().isoformat(timespec="seconds")
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO chats (user_message, assistant_message, created_at)
            VALUES (?, ?, ?)
            """,
            (user_message, assistant_message, now),
        )
        return int(cur.lastrowid)


def get_recent_chats(limit: int = 30) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, user_message, assistant_message, created_at
            FROM chats
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]


def get_chat_by_id(chat_id: int) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, user_message, assistant_message, created_at
            FROM chats
            WHERE id = ?
            """,
            (chat_id,),
        ).fetchone()
    return dict(row) if row else None


def save_message(chat_id: int, note: str = "") -> int:
    now = datetime.utcnow().isoformat(timespec="seconds")
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO saved_messages (chat_id, note, created_at)
            VALUES (?, ?, ?)
            """,
            (chat_id, note.strip(), now),
        )
        return int(cur.lastrowid)


def get_saved_messages() -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                s.id AS save_id,
                s.note,
                s.created_at AS saved_at,
                c.id AS chat_id,
                c.user_message,
                c.assistant_message,
                c.created_at AS chat_created_at
            FROM saved_messages s
            JOIN chats c ON c.id = s.chat_id
            ORDER BY s.id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def delete_saved_message(save_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM saved_messages WHERE id = ?", (save_id,))


def set_setting(key: str, value: str) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO settings (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value = excluded.value
            """,
            (key, value),
        )


def get_setting(key: str, default: str = "") -> str:
    with get_connection() as conn:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
    if not row:
        return default
    return str(row["value"])
