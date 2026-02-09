"""Catalog module - normalizes, deduplicates, and groups articles by ticker."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import date
from pathlib import Path
from typing import Any

from holdup.config import get_catalog_dir, ensure_directories
from holdup.staging import load_staging


@dataclass
class CatalogArticle:
    """Cleaned article ready for consumption."""

    ticker: str
    title: str
    content: str
    url: str
    published_at: str
    source_name: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CatalogArticle":
        """Create a CatalogArticle from a dictionary."""
        return cls(
            ticker=data["ticker"],
            title=data["title"],
            content=data["content"],
            url=data["url"],
            published_at=data["published_at"],
            source_name=data["source_name"],
        )


def get_catalog_file(for_date: date | None = None) -> Path:
    """Get the catalog file path for a given date."""
    if for_date is None:
        for_date = date.today()
    return get_catalog_dir() / f"{for_date.isoformat()}.json"


def build_catalog(for_date: date | None = None) -> dict[str, list[CatalogArticle]]:
    """
    Build the catalog from staging data.

    Reads staging, normalizes, deduplicates by URL, groups by ticker,
    and sorts by recency (most recent first).

    Args:
        for_date: Date for the catalog (defaults to today)

    Returns:
        Dictionary mapping ticker to list of CatalogArticle objects
    """
    # Load raw articles from staging
    raw_articles = load_staging(for_date)

    if not raw_articles:
        return {}

    # Deduplicate by URL
    seen_urls: set[str] = set()
    unique_articles = []
    for article in raw_articles:
        if article.url not in seen_urls:
            seen_urls.add(article.url)
            unique_articles.append(article)

    # Convert to CatalogArticle and group by ticker
    catalog: dict[str, list[CatalogArticle]] = {}
    for raw in unique_articles:
        catalog_article = CatalogArticle(
            ticker=raw.ticker,
            title=raw.title,
            content=raw.content,
            url=raw.url,
            published_at=raw.published_at,
            source_name=raw.source_name,
        )
        if raw.ticker not in catalog:
            catalog[raw.ticker] = []
        catalog[raw.ticker].append(catalog_article)

    # Sort each ticker's articles by recency (most recent first)
    for ticker in catalog:
        catalog[ticker].sort(key=lambda a: a.published_at, reverse=True)

    return catalog


def save_catalog(
    catalog: dict[str, list[CatalogArticle]], for_date: date | None = None
) -> Path:
    """
    Save the catalog to a JSON file.

    Args:
        catalog: Dictionary mapping ticker to list of CatalogArticle objects
        for_date: Date for the catalog file (defaults to today)

    Returns:
        Path to the saved catalog file
    """
    ensure_directories()
    catalog_file = get_catalog_file(for_date)

    # Convert to serializable format
    data = {ticker: [a.to_dict() for a in articles] for ticker, articles in catalog.items()}

    with open(catalog_file, "w") as f:
        json.dump(data, f, indent=2)

    return catalog_file


def load_catalog(for_date: date | None = None) -> dict[str, list[CatalogArticle]]:
    """
    Load the catalog from a JSON file.

    Args:
        for_date: Date for the catalog file (defaults to today)

    Returns:
        Dictionary mapping ticker to list of CatalogArticle objects
    """
    catalog_file = get_catalog_file(for_date)

    if not catalog_file.exists():
        return {}

    with open(catalog_file, "r") as f:
        data = json.load(f)

    return {
        ticker: [CatalogArticle.from_dict(a) for a in articles]
        for ticker, articles in data.items()
    }


def process_catalog(for_date: date | None = None) -> dict[str, list[CatalogArticle]]:
    """
    Build and save the catalog for a given date.

    Args:
        for_date: Date for the catalog (defaults to today)

    Returns:
        The built catalog
    """
    catalog = build_catalog(for_date)
    if catalog:
        save_catalog(catalog, for_date)
    return catalog
