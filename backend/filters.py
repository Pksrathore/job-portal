from __future__ import annotations

from .config import Filters
from .models import Job, MatchResult


def match_job(job: Job, filters: Filters) -> MatchResult | None:
    haystack = " ".join(
        [
            job.title.lower(),
            job.company.lower(),
            job.location.lower(),
            job.description.lower(),
        ]
    )
    reasons: list[str] = []

    if filters.remote_only and "remote" not in job.location.lower():
        return None

    if filters.keywords_any:
        matched_keywords = [kw for kw in filters.keywords_any if kw.lower() in haystack]
        if not matched_keywords:
            return None
        reasons.extend(f"matched keyword '{kw}'" for kw in matched_keywords)

    excluded = [kw for kw in filters.keywords_exclude if kw.lower() in haystack]
    if excluded:
        return None

    if filters.locations_any:
        matched_locations = [loc for loc in filters.locations_any if loc.lower() in haystack]
        if not matched_locations:
            return None
        reasons.extend(f"matched location '{loc}'" for loc in matched_locations)

    return MatchResult(job=job, reasons=reasons)
