from __future__ import annotations

from .models import MatchResult


def print_digest(matches: list[MatchResult]) -> None:
    if not matches:
        print("No new matching jobs found.")
        return

    print(f"Found {len(matches)} new matching jobs:\n")
    for index, match in enumerate(matches, start=1):
        job = match.job
        print(f"{index}. {job.title} at {job.company}")
        print(f"   Location: {job.location}")
        print(f"   Source: {job.provider} ({job.source_label})")
        print(f"   URL: {job.url}")
        print(f"   Why it matched: {', '.join(match.reasons)}")
        print()
