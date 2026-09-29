"""SQLite persistence and URL-based deduplication for MyCS."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from .config import DEFAULT_DATABASE_PATH
from .validate import validate_opportunity


class OpportunityStore:
    """Own a local SQLite database with explicit UTF-8 JSON serialization."""

    def __init__(self, database_path: str | Path = DEFAULT_DATABASE_PATH) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        except sqlite3.Error as error:
            connection.rollback()
            raise RuntimeError(f"Database operation failed: {error}") from error
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connection() as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS opportunities (
                    id INTEGER PRIMARY KEY,
                    url TEXT NOT NULL UNIQUE,
                    title TEXT NOT NULL,
                    organization TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

    def upsert(self, opportunity: dict[str, Any]) -> int:
        """Insert or replace an opportunity by canonical URL and return its identifier."""
        payload = validate_opportunity(opportunity)
        now = datetime.now(timezone.utc).isoformat()
        serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        with self._connection() as connection:
            connection.execute("""
                INSERT INTO opportunities (url, title, organization, payload, created_at, updated_at)
                VALUES (:url, :title, :organization, :payload, :created_at, :updated_at)
                ON CONFLICT(url) DO UPDATE SET
                    title = excluded.title,
                    organization = excluded.organization,
                    payload = excluded.payload,
                    updated_at = excluded.updated_at
            """, {**payload, "payload": serialized, "created_at": now, "updated_at": now})
            row = connection.execute("SELECT id FROM opportunities WHERE url = ?", (payload["url"],)).fetchone()
            if row is None:
                raise RuntimeError("Database did not return the persisted opportunity.")
            return int(row["id"])

    def get_by_url(self, url: str) -> dict[str, Any] | None:
        with self._connection() as connection:
            row = connection.execute("SELECT payload FROM opportunities WHERE url = ?", (url,)).fetchone()
        return json.loads(row["payload"]) if row else None

    def list_recent(self, limit: int = 20) -> list[dict[str, Any]]:
        if limit < 1:
            raise ValueError("limit must be greater than zero")
        with self._connection() as connection:
            rows = connection.execute("SELECT payload FROM opportunities ORDER BY updated_at DESC LIMIT ?", (limit,)).fetchall()
        return [json.loads(row["payload"]) for row in rows]
