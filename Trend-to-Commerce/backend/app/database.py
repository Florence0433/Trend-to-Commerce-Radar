from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Iterator

from backend.app.config import APP_DB_PATH


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    APP_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(APP_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS generation_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                week TEXT,
                topic TEXT,
                mode TEXT NOT NULL,
                status TEXT NOT NULL,
                result_json TEXT,
                error_message TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )


def serialize_job(row: sqlite3.Row | None) -> dict | None:
    if row is None:
        return None
    result = dict(row)
    if result.get("result_json"):
        result["result"] = json.loads(result["result_json"])
    else:
        result["result"] = None
    result.pop("result_json", None)
    return result


def create_generation_job(question: str, week: str | None, topic: str | None, mode: str) -> dict:
    now = utc_now_iso()
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO generation_jobs (
                question, week, topic, mode, status, result_json, error_message, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (question, week, topic, mode, "queued", None, None, now, now),
        )
        job_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM generation_jobs WHERE id = ?", (job_id,)).fetchone()
    return serialize_job(row) or {}


def get_generation_job(job_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM generation_jobs WHERE id = ?", (job_id,)).fetchone()
    return serialize_job(row)


def list_generation_jobs(limit: int = 20) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM generation_jobs ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [serialize_job(row) for row in rows if row is not None]


def update_generation_job_status(
    job_id: int,
    status: str,
    *,
    result: dict | None = None,
    error_message: str | None = None,
    week: str | None = None,
    topic: str | None = None,
) -> None:
    now = utc_now_iso()
    result_json = json.dumps(result, ensure_ascii=False) if result is not None else None
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE generation_jobs
            SET status = ?,
                result_json = COALESCE(?, result_json),
                error_message = ?,
                week = COALESCE(?, week),
                topic = COALESCE(?, topic),
                updated_at = ?
            WHERE id = ?
            """,
            (status, result_json, error_message, week, topic, now, job_id),
        )
