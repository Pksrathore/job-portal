"""Export jobs to JSON for GitHub Pages frontend."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from .models import Job


def export_jobs(jobs: list[Job], output_path: Path, include_timestamp: bool = True) -> None:
    """Export jobs to JSON file for GitHub Pages frontend.

    Args:
        jobs: List of jobs to export
        output_path: Path to output JSON file
        include_timestamp: Whether to include export timestamp
    """
    # Ensure parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert jobs to dictionaries
    jobs_data = [job_to_dict(job) for job in jobs]

    # Build export payload
    export_data = {
        "exported_at": datetime.utcnow().isoformat() + "Z" if include_timestamp else None,
        "total_jobs": len(jobs_data),
        "jobs": jobs_data,
    }

    # Write JSON file
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)


def job_to_dict(job: Job) -> dict:
    """Convert Job object to dictionary for JSON export.

    Args:
        job: Job object to convert

    Returns:
        Dictionary representation of job
    """
    return {
        "id": job.external_id,
        "provider": job.provider,
        "source": job.source_label,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "url": job.url,
        "posted_at": job.updated_at,
        "description": job.description,
        # Add frontend-friendly fields
        "is_remote": "remote" in job.location.lower(),
        "timestamp": parse_timestamp(job.updated_at) if job.updated_at else 0,
    }


def parse_timestamp(timestamp: str) -> int:
    """Parse timestamp string to Unix timestamp.

    Args:
        timestamp: ISO format timestamp or Unix timestamp string

    Returns:
        Unix timestamp as integer
    """
    if not timestamp:
        return 0

    # Try parsing as Unix timestamp first
    try:
        return int(timestamp)
    except ValueError:
        pass

    # Try ISO format
    formats = [
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(timestamp, fmt)
            return int(dt.timestamp())
        except ValueError:
            continue

    return 0


def load_exported_jobs(input_path: Path) -> list[dict]:
    """Load previously exported jobs from JSON file.

    Args:
        input_path: Path to JSON file

    Returns:
        List of job dictionaries
    """
    if not input_path.exists():
        return []

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data.get("jobs", [])
