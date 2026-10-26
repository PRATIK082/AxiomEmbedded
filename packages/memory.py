"""Local SQLite-backed memory store for Axiom (E1).

Stores sessions, facts, and project knowledge. Never stores secrets (E5):
a naive secret scanner redacts values matching common token patterns.
"""
from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|token|secret|password|passwd)\s*[:=]\s*\S+"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{30,}"),
]


def redact(text: str) -> str:
    out = text
    for pat in SECRET_PATTERNS:
        out = pat.sub("[REDACTED]", out)
    return out


class MemoryStore:
    def __init__(self, db_path: str | Path):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init()

    def _init(self) -> None:
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scope TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            started_at TEXT NOT NULL,
            ended_at TEXT,
            summary TEXT
        );
        CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL,
            token TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_knowledge_token ON knowledge(token);
        """)
        self.conn.commit()

    def put_fact(self, scope: str, key: str, value: str) -> int:
        value = redact(value)
        now = datetime.now(timezone.utc).isoformat()
        cur = self.conn.execute(
            "INSERT INTO facts (scope, key, value, created_at) VALUES (?,?,?,?)",
            (scope, key, value, now))
        self.conn.commit()
        return cur.lastrowid

    def get_facts(self, scope: str | None = None) -> list[dict]:
        if scope:
            rows = self.conn.execute(
                "SELECT * FROM facts WHERE scope=?", (scope,)).fetchall()
        else:
            rows = self.conn.execute("SELECT * FROM facts").fetchall()
        return [dict(r) for r in rows]

    def search_facts(self, query: str) -> list[dict]:
        q = f"%{query}%"
        rows = self.conn.execute(
            "SELECT * FROM facts WHERE key LIKE ? OR value LIKE ?", (q, q)).fetchall()
        return [dict(r) for r in rows]

    def start_session(self, session_id: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        self.conn.execute("INSERT OR REPLACE INTO sessions (id, started_at) VALUES (?,?)",
                          (session_id, now))
        self.conn.commit()

    def end_session(self, session_id: str, summary: str = "") -> None:
        now = datetime.now(timezone.utc).isoformat()
        self.conn.execute("UPDATE sessions SET ended_at=?, summary=? WHERE id=?",
                          (now, redact(summary), session_id))
        self.conn.commit()

    def list_sessions(self) -> list[dict]:
        rows = self.conn.execute("SELECT * FROM sessions ORDER BY started_at DESC").fetchall()
        return [dict(r) for r in rows]

    def index_path(self, path: str) -> int:
        """Index a file's tokens into the knowledge table."""
        from pathlib import Path as _P

        p = _P(path)
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return 0
        toks = set(__import__("re").findall(r"[a-z0-9]+", text.lower()))
        now = datetime.now(timezone.utc).isoformat()
        n = 0
        for t in toks:
            self.conn.execute(
                "INSERT INTO knowledge (path, token, created_at) VALUES (?,?,?)",
                (str(p), t, now))
            n += 1
        self.conn.commit()
        return n

    def search_knowledge(self, query: str, limit: int = 20) -> list[dict]:
        toks = set(__import__("re").findall(r"[a-z0-9]+", query.lower()))
        if not toks:
            return []
        placeholders = ",".join("?" for _ in toks)
        rows = self.conn.execute(
            f"SELECT DISTINCT path FROM knowledge WHERE token IN ({placeholders}) "
            "GROUP BY path ORDER BY COUNT(*) DESC LIMIT ?",
            (*toks, limit)).fetchall()
        return [{"path": r["path"]} for r in rows]

    def close(self) -> None:
        self.conn.close()
