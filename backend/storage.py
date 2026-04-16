from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .models import Job


class JobStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    external_id TEXT PRIMARY KEY,
                    provider TEXT NOT NULL,
                    source_label TEXT NOT NULL,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    location TEXT NOT NULL,
                    url TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    description TEXT NOT NULL,
                    seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

    def has_seen(self, external_id: str) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT 1 FROM jobs WHERE external_id = ? LIMIT 1", (external_id,)
            ).fetchone()
        return row is not None

    def save(self, job: Job) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO jobs (
                    external_id, provider, source_label, title, company,
                    location, url, updated_at, description
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job.external_id,
                    job.provider,
                    job.source_label,
                    job.title,
                    job.company,
                    job.location,
                    job.url,
                    job.updated_at,
                    job.description,
                ),
            )

    def get_all_jobs(self) -> list[Job]:
        """Get all stored jobs."""
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT external_id, provider, source_label, title, company,
                       location, url, updated_at, description
                FROM jobs
                ORDER BY updated_at DESC
                """
            ).fetchall()

        return [
            Job(
                external_id=row[0],
                provider=row[1],
                source_label=row[2],
                title=row[3],
                company=row[4],
                location=row[5],
                url=row[6],
                updated_at=row[7],
                description=row[8],
            )
            for row in rows
        ]

    def get_jobs_for_export(self, limit: int = 100) -> list[Job]:
        """Get recent jobs for export to GitHub Pages."""
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT external_id, provider, source_label, title, company,
                       location, url, updated_at, description
                FROM jobs
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [
            Job(
                external_id=row[0],
                provider=row[1],
                source_label=row[2],
                title=row[3],
                company=row[4],
                location=row[5],
                url=row[6],
                updated_at=row[7],
                description=row[8],
            )
            for row in rows
        ]
