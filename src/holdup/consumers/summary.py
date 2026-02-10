"""Summary consumer - generates plain-English digests using GPT-4o-mini."""

from pathlib import Path

from openai import OpenAI

from holdup.catalog import CatalogArticle
from holdup.config import get_openai_api_key
from holdup.consumers.base import BaseConsumer


def get_project_output_dir() -> Path:
    """Get the project's output directory."""
    # Go up from src/holdup/consumers/summary.py to project root
    project_root = Path(__file__).parent.parent.parent.parent
    output_dir = project_root / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

SYSTEM_PROMPT = """You are a financial news assistant for casual retail investors. Analyze news for the given stock ticker using this format:

**Sentiment:** [Bullish / Bearish / Neutral]

**Credibility:** [Is this confirmed news or speculation? Are sources reliable?]

**Short term:** [What might happen in the next days/weeks?]

**Long term:** [What might this mean over months/years?]

**Pros:** [Reasons this news is good for holders]
**Cons:** [Reasons to be concerned]

Rules:
- If no articles are directly about this stock (just passing mentions), say "No direct news" and skip the analysis
- Be concise - one sentence per field
- Do NOT add info not in the articles
- Do NOT give buy/sell advice"""


class SummaryConsumer(BaseConsumer):
    """Consumer that generates plain-English summaries using GPT-4o-mini."""

    def __init__(self) -> None:
        api_key = get_openai_api_key()
        if not api_key:
            raise ValueError(
                "OpenAI API key not found. Run 'holdup setup' first."
            )
        self.client = OpenAI(api_key=api_key)

    def _summarize_ticker(self, ticker: str, articles: list[CatalogArticle]) -> str:
        """
        Generate a summary for a single ticker.

        Args:
            ticker: Stock ticker symbol
            articles: List of articles for this ticker

        Returns:
            Plain-English summary string
        """
        # Build the articles context
        articles_text = ""
        for i, article in enumerate(articles, 1):
            articles_text += f"\n--- Article {i} ---\n"
            articles_text += f"Title: {article.title}\n"
            articles_text += f"Source: {article.source_name}\n"
            articles_text += f"Published: {article.published_at}\n"
            articles_text += f"Content: {article.content}\n"

        user_prompt = f"Ticker: {ticker}\n\nRecent news articles:{articles_text}"

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.3,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
            )
            return response.choices[0].message.content or "No summary generated."
        except Exception as e:
            return f"Error generating summary: {e}"

    def consume(self, catalog: dict[str, list[CatalogArticle]], date_str: str) -> None:
        """
        Generate summaries for all tickers and save to output file.

        Args:
            catalog: Dictionary mapping ticker to list of CatalogArticle objects
            date_str: Date string in ISO format (YYYY-MM-DD)
        """
        if not catalog:
            print("No articles to summarize.")
            return

        output_dir = get_project_output_dir()
        output_file = output_dir / f"summary_{date_str}.md"

        summaries: list[str] = []

        print(f"\nGenerating summaries for {len(catalog)} tickers...")

        for ticker, articles in sorted(catalog.items()):
            print(f"  Summarizing {ticker} ({len(articles)} articles)...")
            summary = self._summarize_ticker(ticker, articles)

            # Format for both stdout and file
            ticker_section = f"## {ticker}\n\n{summary}\n"
            summaries.append(ticker_section)

            # Print to stdout
            print(f"\n{'='*50}")
            print(f"  {ticker}")
            print(f"{'='*50}")
            print(summary)
            print()

        # Save to file
        header = f"# Stock News Summary - {date_str}\n\n"
        content = header + "\n".join(summaries)

        with open(output_file, "w") as f:
            f.write(content)

        print(f"\nSummary saved to: {output_file}")
