"""Instincts: confidence-scored, project-scoped learned patterns (E3).

Adapted from ECC's continuous-learning-v2: each instinct has a trigger,
action, confidence (0.3-0.9), scope (project/global), and evidence count.
Promotion moves a project instinct to global when confidence >= threshold.
"""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DB = ".axiom/instincts.db"


class InstinctStore:
    def __init__(self, db_path: str | Path = DEFAULT_DB):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS instincts (
            id TEXT PRIMARY KEY,
            trigger TEXT NOT NULL,
            action TEXT NOT NULL,
            confidence REAL NOT NULL,
            scope TEXT NOT NULL,
            project TEXT,
            evidence_count INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """)
        self.conn.commit()

    def add(self, instinct_id: str, trigger: str, action: str,
            confidence: float = 0.5, scope: str = "project",
            project: str | None = None) -> dict:
        confidence = max(0.3, min(0.9, confidence))
        now = datetime.now(timezone.utc).isoformat()
        existing = self.conn.execute("SELECT * FROM instincts WHERE id=?", (instinct_id,)).fetchone()
        if existing:
            new_conf = min(0.9, existing["confidence"] + 0.05)
            self.conn.execute(
                "UPDATE instincts SET confidence=?, evidence_count=evidence_count+1, updated_at=? WHERE id=?",
                (new_conf, now, instinct_id))
        else:
            self.conn.execute(
                "INSERT INTO instincts (id, trigger, action, confidence, scope, project, created_at, updated_at) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (instinct_id, trigger, action, confidence, scope, project, now, now))
        self.conn.commit()
        row = self.conn.execute("SELECT * FROM instincts WHERE id=?", (instinct_id,)).fetchone()
        return dict(row)

    def list(self, scope: str | None = None, project: str | None = None,
             min_confidence: float = 0.0) -> list[dict]:
        q = "SELECT * FROM instincts WHERE confidence >= ?"
        params: list = [min_confidence]
        if scope:
            q += " AND scope=?"
            params.append(scope)
        if project:
            q += " AND (project=? OR scope='global')"
            params.append(project)
        rows = self.conn.execute(q, params).fetchall()
        return [dict(r) for r in rows]

    def promote(self, instinct_id: str, threshold: float = 0.8) -> dict:
        row = self.conn.execute("SELECT * FROM instincts WHERE id=?", (instinct_id,)).fetchone()
        if not row:
            return {"status": "error", "message": "not found"}
        if row["confidence"] < threshold:
            return {"status": "not_ready", "confidence": row["confidence"],
                    "threshold": threshold}
        self.conn.execute("UPDATE instincts SET scope='global', project=NULL WHERE id=?",
                          (instinct_id,))
        self.conn.commit()
        return {"status": "promoted", "id": instinct_id}

    def close(self) -> None:
        self.conn.close()
