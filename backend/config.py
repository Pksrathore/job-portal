from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Filters:
    keywords_any: list[str]
    keywords_exclude: list[str]
    locations_any: list[str]
    seniority_levels: list[str] | None = None
    job_types: list[str] | None = None
    remote_only: bool = True


@dataclass(slots=True)
class SourceConfig:
    provider: str
    label: str
    token: str | None = None
    slug: str | None = None
    query: str = "senior analyst strategy"
    num_pages: int = 1
    remote_only: bool = True


@dataclass(slots=True)
class AppConfig:
    database_path: Path
    filters: Filters
    sources: list[SourceConfig]
    apis: dict | None = None


def load_config(path: str) -> AppConfig:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    filters = Filters(**raw["filters"])
    sources = [SourceConfig(**item) for item in raw["sources"]]
    database_path = Path(path).parent / raw["database_path"]
    apis = raw.get("apis", {})
    return AppConfig(database_path=database_path, filters=filters, sources=sources, apis=apis)
