"""Crawlers module - fetches raw articles from news APIs."""

import time

from holdup.crawlers.base import RawArticle, BaseCrawler
from holdup.crawlers.alpaca import AlpacaCrawler

__all__ = ["RawArticle", "BaseCrawler", "AlpacaCrawler", "crawl_all"]


def crawl_all(tickers: list[str], days_back: int = 1) -> list[RawArticle]:
    """
    Crawl all tickers using all available crawlers.

    Args:
        tickers: List of ticker symbols
        days_back: Number of days to look back for articles

    Returns:
        List of all RawArticle objects from all crawlers
    """
    all_articles: list[RawArticle] = []

    # Initialize crawlers
    try:
        alpaca = AlpacaCrawler()
    except ValueError as e:
        print(f"Error: {e}")
        return []

    for i, ticker in enumerate(tickers):
        print(f"  Fetching news for {ticker}...")
        articles = alpaca.fetch(ticker, days_back)
        all_articles.extend(articles)
        print(f"    Found {len(articles)} articles")

        # Rate limiting: 0.3s delay between tickers (except for last one)
        if i < len(tickers) - 1:
            time.sleep(0.3)

    return all_articles
