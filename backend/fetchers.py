from __future__ import annotations

import json
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .config import SourceConfig
from .models import Job
from .sources.jsearch import fetch_jsearch_jobs


def fetch_jobs(source: SourceConfig, api_keys: dict | None = None) -> list[Job]:
    provider = source.provider.lower()
    if provider == "greenhouse":
        return _fetch_greenhouse(source)
    if provider == "lever":
        return _fetch_lever(source)
    if provider == "ashby":
        return _fetch_ashby(source)
    if provider == "jsearch":
        return _fetch_jsearch(source, api_keys or {})
    raise ValueError(f"Unsupported provider: {source.provider}")


def _read_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": "job-opportunity-agent/0.1"})
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def _fetch_greenhouse(source: SourceConfig) -> list[Job]:
    if not source.token:
        raise ValueError("Greenhouse source requires 'token'")
    url = f"https://boards-api.greenhouse.io/v1/boards/{source.token}/jobs?content=true"
    payload = _read_json(url)
    jobs: list[Job] = []
    for item in payload.get("jobs", []):
        location = (item.get("location") or {}).get("name", "Unknown")
        jobs.append(
            Job(
                external_id=f"greenhouse:{item['id']}",
                provider="greenhouse",
                source_label=source.label,
                title=item.get("title", "").strip(),
                company=source.label,
                location=location,
                url=item.get("absolute_url", ""),
                updated_at=item.get("updated_at", ""),
                description=_strip_html(item.get("content", "")),
            )
        )
    return jobs


def _fetch_lever(source: SourceConfig) -> list[Job]:
    if not source.slug:
        raise ValueError("Lever source requires 'slug'")
    query = urlencode({"mode": "json"})
    url = f"https://api.lever.co/v0/postings/{source.slug}?{query}"
    payload = _read_json(url)
    jobs: list[Job] = []
    for item in payload:
        categories = item.get("categories", {})
        commitment = categories.get("commitment", "")
        team = categories.get("team", "")
        description = " ".join(
            part for part in [item.get("descriptionPlain", ""), commitment, team] if part
        )
        jobs.append(
            Job(
                external_id=f"lever:{item['id']}",
                provider="lever",
                source_label=source.label,
                title=item.get("text", "").strip(),
                company=source.label,
                location=item.get("categories", {}).get("location", "Unknown"),
                url=item.get("hostedUrl", ""),
                updated_at=item.get("createdAt", ""),
                description=description,
            )
        )
    return jobs


def _fetch_ashby(source: SourceConfig) -> list[Job]:
    if not source.slug:
        raise ValueError("Ashby source requires 'slug'")
    url = f"https://jobs.ashbyhq.com/api/non-user-graphql?op=apiJobBoardWithTeams&organizationHostedJobsPageName={source.slug}"
    payload = _read_json(url)
    jobs: list[Job] = []
    for team in payload.get("data", {}).get("jobBoard", {}).get("jobPostingsGroupedByTeam", []):
        for item in team.get("jobPostings", []):
            location_parts = [entry.get("label", "") for entry in item.get("location", [])]
            jobs.append(
                Job(
                    external_id=f"ashby:{item['id']}",
                    provider="ashby",
                    source_label=source.label,
                    title=item.get("title", "").strip(),
                    company=source.label,
                    location=", ".join(part for part in location_parts if part) or "Unknown",
                    url=f"https://jobs.ashbyhq.com/{source.slug}/{item.get('id')}",
                    updated_at=item.get("publishedDate", ""),
                    description=item.get("descriptionPlain", ""),
                )
            )
    return jobs


def _strip_html(value: str) -> str:
    in_tag = False
    output: list[str] = []
    for char in value:
        if char == "<":
            in_tag = True
            continue
        if char == ">":
            in_tag = False
            output.append(" ")
            continue
        if not in_tag:
            output.append(char)
    return " ".join("".join(output).split())


def _fetch_jsearch(source: SourceConfig, api_keys: dict) -> list[Job]:
    """Fetch jobs from JSearch API."""
    api_key = api_keys.get("jsearch_api_key")
    if not api_key:
        print(
            f"Warning: JSearch API key not configured. Skipping {source.label}.",
            file=__import__("sys").stderr,
        )
        return []

    query = getattr(source, "query", "senior analyst strategy")
    num_pages = getattr(source, "num_pages", 1)
    remote_only = getattr(source, "remote_only", True)

    return fetch_jsearch_jobs(
        api_key=api_key,
        query=query,
        num_pages=num_pages,
        remote_only=remote_only,
    )
