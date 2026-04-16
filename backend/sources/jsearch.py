"""JSearch API integration for aggregating jobs from multiple platforms."""

from __future__ import annotations

import json
import urllib.request
from typing import Any

from ..models import Job


class JSearchJobFetcher:
    """Fetch jobs from JSearch API which aggregates LinkedIn, Indeed, Glassdoor, etc."""

    BASE_URL = "https://jsearch.p.rapidapi.com/search"

    def __init__(self, api_key: str):
        """Initialize with JSearch API key.

        Args:
            api_key: RapidAPI key for JSearch API
        """
        self.api_key = api_key

    def fetch_jobs(
        self,
        query: str = "",
        location: str = "",
        num_pages: int = 1,
        job_types: list[str] | None = None,
        remote_only: bool = False,
    ) -> list[Job]:
        """Fetch jobs from JSearch API.

        Args:
            query: Search query (e.g., "senior analyst strategy")
            location: Location filter (e.g., "Remote", "United States")
            num_pages: Number of pages to fetch (max 10)
            job_types: List of job types (fulltime, parttime, contract, internship)
            remote_only: Filter for remote jobs only

        Returns:
            List of Job objects
        """
        jobs: list[Job] = []

        for page in range(1, num_pages + 1):
            params = {
                "query": query,
                "page": str(page),
                "num_pages": "1",
            }

            if location:
                params["location"] = location

            if job_types:
                params["job_types"] = ",".join(job_types)

            if remote_only:
                params["remote_jobs_only"] = "true"

            url = self._build_url(params)
            data = self._fetch(url)

            for item in data.get("data", []):
                job = self._parse_job(item)
                if job:
                    jobs.append(job)

        return jobs

    def _build_url(self, params: dict[str, str]) -> str:
        """Build URL with query parameters."""
        query_string = "&".join(f"{key}={value}" for key, value in params.items())
        return f"{self.BASE_URL}?{query_string}"

    def _fetch(self, url: str) -> dict[str, Any]:
        """Fetch data from API."""
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
        }
        request = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))

    def _parse_job(self, item: dict[str, Any]) -> Job | None:
        """Parse a job item from API response."""
        try:
            employer = item.get("employer", {})
            if isinstance(employer, dict):
                company_name = employer.get("name", "Unknown")
            else:
                company_name = str(employer) if employer else "Unknown"

            # Get first job posting detail
            postings = item.get("job_postings", [])
            posting = postings[0] if postings else {}

            # Extract location
            locations = item.get("job_locations", [])
            location = locations[0].get("name", "Remote") if locations else "Remote"

            # Build description
            description_parts = []
            if item.get("job_description"):
                description_parts.append(item["job_description"])
            if posting.get("highlights"):
                highlights = posting["highlights"]
                if isinstance(highlights, dict):
                    for key, values in highlights.items():
                        if isinstance(values, list):
                            description_parts.append(f"{key}: " + ", ".join(values))

            return Job(
                external_id=f"jsearch:{item.get('job_id', '')}",
                provider="jsearch",
                source_label="JSearch",
                title=item.get("job_title", "").strip(),
                company=company_name,
                location=location,
                url=item.get("job_apply_link", "") or item.get("job_apply_is_direct", False),
                updated_at=item.get("job_posted_at_timestamp", ""),
                description=" ".join(description_parts),
            )
        except (KeyError, TypeError, IndexError):
            return None


def fetch_jsearch_jobs(
    api_key: str,
    query: str = "",
    location: str = "",
    num_pages: int = 1,
    job_types: list[str] | None = None,
    remote_only: bool = False,
) -> list[Job]:
    """Convenience function to fetch jobs from JSearch API.

    Args:
        api_key: JSearch API key
        query: Search query
        location: Location filter
        num_pages: Number of pages to fetch
        job_types: Job types to filter
        remote_only: Remote jobs only

    Returns:
        List of Job objects
    """
    fetcher = JSearchJobFetcher(api_key)
    return fetcher.fetch_jobs(
        query=query,
        location=location,
        num_pages=num_pages,
        job_types=job_types,
        remote_only=remote_only,
    )
