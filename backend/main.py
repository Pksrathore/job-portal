from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import load_config
from .fetchers import fetch_jobs
from .filters import match_job
from .notifier import print_digest
from .storage import JobStore
from .export import export_jobs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Track matching job opportunities.")
    parser.add_argument("--config", required=True, help="Path to config JSON file.")
    parser.add_argument(
        "--search",
        action="store_true",
        help="Run on-demand search and export results for GitHub Pages.",
    )
    parser.add_argument(
        "--query",
        type=str,
        default="",
        help="Search query for on-demand search (e.g., 'senior analyst strategy').",
    )
    parser.add_argument(
        "--location",
        type=str,
        default="",
        help="Location filter for on-demand search (e.g., 'Remote', 'United States').",
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export jobs to JSON for GitHub Pages.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config(args.config)
    store = JobStore(config.database_path)
    matches = []

    # Get API keys from config
    api_keys = config.apis or {}

    for source in config.sources:
        try:
            # Override query if provided via CLI
            if args.query and hasattr(source, "query"):
                source.query = args.query

            jobs = fetch_jobs(source, api_keys)
        except Exception as exc:  # noqa: BLE001
            print(f"Failed to fetch jobs from {source.label}: {exc}", file=sys.stderr)
            continue

        for job in jobs:
            if store.has_seen(job.external_id):
                continue
            matched = match_job(job, config.filters)
            store.save(job)
            if matched:
                matches.append(matched)

    print_digest(matches)

    # Export to JSON if requested or if --search flag is used
    if args.search or args.export:
        all_jobs = store.get_all_jobs()
        export_path = Path(config.database_path).parent / "export" / "jobs.json"
        export_jobs(all_jobs, export_path)
        print(f"\nExported {len(all_jobs)} jobs to {export_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
