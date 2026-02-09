"""Staging module - appends raw articles to daily JSON files."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from holdup.config import get_staging_dir, ensure_directories
from holdup.crawlers.base import RawArticle


def get_staging_file(for_date: date | None = None) -> Path:
    """Get the staging file path for a given date."""
    if for_date is None:
        for_date = date.today()
    return get_staging_dir() / f"{for_date.isoformat()}.json"


def append_to_staging(articles: list[RawArticle], for_date: date | None = None) -> int:
    """
    Append raw articles to the staging file for the given date.

    This is append-only - articles are added to the existing file.

    Args:
        articles: List of RawArticle objects to append
        for_date: Date for the staging file (defaults to today)

    Returns:
        Total number of articles in the staging file after append
    """
    ensure_directories()
    staging_file = get_staging_file(for_date)

    # Load existing articles if file exists
    existing: list[dict] = []
    if staging_file.exists():
        with open(staging_file, "r") as f:
            existing = json.load(f)

    # Append new articles
    for article in articles:
        existing.append(article.to_dict())

    # Write back
    with open(staging_file, "w") as f:
        json.dump(existing, f, indent=2)

    return len(existing)


def load_staging(for_date: date | None = None) -> list[RawArticle]:
    """
    Load all raw articles from the staging file for a given date.

    Args:
        for_date: Date for the staging file (defaults to today)

    Returns:
        List of RawArticle objects
    """
    staging_file = get_staging_file(for_date)

    if not staging_file.exists():
        return []

    with open(staging_file, "r") as f:
        data = json.load(f)

    return [RawArticle.from_dict(item) for item in data]
