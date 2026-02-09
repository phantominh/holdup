"""CLI entry point for holdup."""

from datetime import date

import click

from holdup.config import (
    add_tickers,
    remove_ticker,
    load_watchlist,
    save_env,
    get_alpaca_credentials,
    get_openai_api_key,
    ensure_directories,
)
from holdup.crawlers import crawl_all
from holdup.staging import append_to_staging
from holdup.catalog import process_catalog, load_catalog
from holdup.consumers import SummaryConsumer


@click.group()
@click.version_option()
def cli() -> None:
    """holdup - Stock news for casual investors, explained in plain English."""
    pass


@cli.command()
def setup() -> None:
    """Interactive setup for API keys."""
    click.echo("Welcome to holdup setup!\n")
    click.echo("You'll need API keys from:")
    click.echo("  - Alpaca (https://alpaca.markets/) - for stock news")
    click.echo("  - OpenAI (https://platform.openai.com/) - for summaries\n")

    # Get existing values if any
    existing_alpaca_key, existing_alpaca_secret = get_alpaca_credentials()
    existing_openai = get_openai_api_key()

    # Alpaca API Key
    prompt = "Alpaca API Key"
    if existing_alpaca_key:
        prompt += f" [{existing_alpaca_key[:8]}...]"
    alpaca_key = click.prompt(prompt, default=existing_alpaca_key or "", show_default=False)

    # Alpaca API Secret
    prompt = "Alpaca API Secret"
    if existing_alpaca_secret:
        prompt += f" [{existing_alpaca_secret[:8]}...]"
    alpaca_secret = click.prompt(prompt, default=existing_alpaca_secret or "", show_default=False)

    # OpenAI API Key
    prompt = "OpenAI API Key"
    if existing_openai:
        prompt += f" [{existing_openai[:8]}...]"
    openai_key = click.prompt(prompt, default=existing_openai or "", show_default=False)

    # Save
    save_env(alpaca_key, alpaca_secret, openai_key)
    ensure_directories()

    click.echo("\nConfiguration saved to ~/.holdup/.env")
    click.echo("Run 'holdup add AAPL MSFT' to add tickers to your watchlist.")


@cli.command()
@click.argument("tickers", nargs=-1, required=True)
def add(tickers: tuple[str, ...]) -> None:
    """Add tickers to your watchlist."""
    if not tickers:
        click.echo("Please provide at least one ticker.")
        return

    updated = add_tickers(list(tickers))
    added = [t.upper() for t in tickers]
    click.echo(f"Added: {', '.join(added)}")
    click.echo(f"Watchlist: {', '.join(updated)}")


@cli.command()
@click.argument("ticker", required=True)
def remove(ticker: str) -> None:
    """Remove a ticker from your watchlist."""
    if remove_ticker(ticker):
        click.echo(f"Removed: {ticker.upper()}")
        remaining = load_watchlist()
        if remaining:
            click.echo(f"Watchlist: {', '.join(remaining)}")
        else:
            click.echo("Watchlist is now empty.")
    else:
        click.echo(f"Ticker {ticker.upper()} not in watchlist.")


@cli.command("list")
def list_tickers() -> None:
    """Show your watchlist."""
    watchlist = load_watchlist()
    if watchlist:
        click.echo(f"Watchlist ({len(watchlist)} tickers):")
        for ticker in watchlist:
            click.echo(f"  {ticker}")
    else:
        click.echo("Watchlist is empty. Run 'holdup add AAPL MSFT' to add tickers.")


@cli.command()
@click.argument("tickers", nargs=-1)
def check(tickers: tuple[str, ...]) -> None:
    """Full pipeline: crawl → stage → catalog → summary."""
    # Get tickers from args or watchlist
    ticker_list = list(tickers) if tickers else load_watchlist()

    if not ticker_list:
        click.echo("No tickers specified and watchlist is empty.")
        click.echo("Run 'holdup add AAPL MSFT' to add tickers, or specify them directly.")
        return

    today = date.today()
    date_str = today.isoformat()

    click.echo(f"Checking {len(ticker_list)} tickers: {', '.join(ticker_list)}")
    click.echo(f"Date: {date_str}\n")

    # Stage 1-2: Crawl and stage
    click.echo("Stage 1-2: Fetching news...")
    articles = crawl_all(ticker_list)

    if articles:
        total = append_to_staging(articles, today)
        click.echo(f"\nStaged {len(articles)} new articles (total in staging: {total})")
    else:
        click.echo("\nNo new articles found.")

    # Stage 3: Catalog
    click.echo("\nStage 3: Building catalog...")
    catalog = process_catalog(today)

    if not catalog:
        click.echo("No articles to catalog.")
        return

    total_articles = sum(len(articles) for articles in catalog.values())
    click.echo(f"Catalog: {len(catalog)} tickers, {total_articles} unique articles")

    # Stage 4: Summary
    click.echo("\nStage 4: Generating summaries...")
    try:
        consumer = SummaryConsumer()
        consumer.consume(catalog, date_str)
    except ValueError as e:
        click.echo(f"Error: {e}")


@cli.command()
@click.argument("tickers", nargs=-1)
def crawl(tickers: tuple[str, ...]) -> None:
    """Run stages 1-2 only (crawl and stage)."""
    ticker_list = list(tickers) if tickers else load_watchlist()

    if not ticker_list:
        click.echo("No tickers specified and watchlist is empty.")
        return

    today = date.today()
    click.echo(f"Crawling {len(ticker_list)} tickers: {', '.join(ticker_list)}\n")

    articles = crawl_all(ticker_list)

    if articles:
        total = append_to_staging(articles, today)
        click.echo(f"\nStaged {len(articles)} new articles (total in staging: {total})")
    else:
        click.echo("\nNo articles found.")


@cli.command()
def catalog() -> None:
    """Run stage 3 only (build catalog from today's staging)."""
    today = date.today()
    click.echo(f"Building catalog for {today.isoformat()}...\n")

    catalog_data = process_catalog(today)

    if not catalog_data:
        click.echo("No articles to catalog. Run 'holdup crawl' first.")
        return

    total_articles = sum(len(articles) for articles in catalog_data.values())
    click.echo(f"Catalog: {len(catalog_data)} tickers, {total_articles} unique articles")

    for ticker, articles in sorted(catalog_data.items()):
        click.echo(f"  {ticker}: {len(articles)} articles")


@cli.command()
def resummarize() -> None:
    """Run stage 4 only (re-run summary on existing catalog)."""
    today = date.today()
    date_str = today.isoformat()

    click.echo(f"Loading catalog for {date_str}...")
    catalog_data = load_catalog(today)

    if not catalog_data:
        click.echo("No catalog found. Run 'holdup check' or 'holdup catalog' first.")
        return

    try:
        consumer = SummaryConsumer()
        consumer.consume(catalog_data, date_str)
    except ValueError as e:
        click.echo(f"Error: {e}")


if __name__ == "__main__":
    cli()
