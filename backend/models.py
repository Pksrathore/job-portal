from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Job:
    external_id: str
    provider: str
    source_label: str
    title: str
    company: str
    location: str
    url: str
    updated_at: str
    description: str


@dataclass(slots=True)
class MatchResult:
    job: Job
    reasons: list[str]
