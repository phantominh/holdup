"""Alpaca News API crawler."""

from datetime import datetime, timedelta, timezone

from alpaca.data.historical.news import NewsClient
from alpaca.data.requests import NewsRequest

from holdup.config import get_alpaca_credentials
from holdup.crawlers.base import BaseCrawler, RawArticle


class AlpacaCrawler(BaseCrawler):
    """Crawler for Alpaca News API."""

    def __init__(self) -> None:
        api_key, api_secret = get_alpaca_credentials()
        if not api_key or not api_secret:
            raise ValueError(
                "Alpaca API credentials not found. Run 'holdup setup' first."
            )
        self.client = NewsClient(api_key=api_key, secret_key=api_secret)

    def fetch(self, ticker: str, days_back: int = 1) -> list[RawArticle]:
        """
        Fetch news articles for a ticker from Alpaca News API.

        Args:
            ticker: Stock ticker symbol (e.g., "AAPL")
            days_back: Number of days to look back for articles

        Returns:
            List of RawArticle objects
        """
        now = datetime.now(timezone.utc)
        start = now - timedelta(days=days_back)

        request = NewsRequest(
            symbols=ticker.upper(),
            start=start,
            end=now,
            limit=50,  # Max articles per request
        )

        try:
            response = self.client.get_news(request)
        except Exception as e:
            # Log error but don't crash - return empty list
            print(f"  Warning: Failed to fetch news for {ticker}: {e}")
            return []

        articles = []
        news_items = response.data.get("news", [])
        for news in news_items:
            # Use summary as content if available, otherwise use headline
            summary = (news.summary or "").strip()
            content = summary if summary else (news.headline or "")

            article = RawArticle(
                source_api="alpaca",
                ticker=ticker.upper(),
                title=news.headline or "",
                content=content,
                url=news.url or "",
                published_at=news.created_at.isoformat() if news.created_at else "",
                source_name=news.source or "",
            )
            articles.append(article)

        return articles
