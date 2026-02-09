"""Base classes and data models for crawlers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class RawArticle:
    """Raw article fetched from a news API."""

    source_api: str         # e.g., "alpaca"
    ticker: str             # e.g., "AAPL"
    title: str
    content: str            # Full body if available, else snippet
    url: str
    published_at: str       # ISO 8601 format
    source_name: str        # e.g., "Benzinga"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RawArticle":
        """Create a RawArticle from a dictionary."""
        return cls(
            source_api=data["source_api"],
            ticker=data["ticker"],
            title=data["title"],
            content=data["content"],
            url=data["url"],
            published_at=data["published_at"],
            source_name=data["source_name"],
        )


class BaseCrawler(ABC):
    """Abstract base class for news crawlers."""

    @abstractmethod
    def fetch(self, ticker: str, days_back: int = 1) -> list[RawArticle]:
        """
        Fetch articles for a given ticker.

        Args:
            ticker: Stock ticker symbol (e.g., "AAPL")
            days_back: Number of days to look back for articles

        Returns:
            List of RawArticle objects
        """
        pass
