# holdup

A CLI tool that monitors your stock tickers, fetches recent news, and tells you what's happening in plain English. Built for casual investors who don't follow financial news.

## How it works

```
┌───────────┐     ┌───────────┐     ┌───────────┐     ┌───────────┐
│ CRAWLERS  │────▶│  STAGING  │────▶│  CATALOG  │────▶│ CONSUMERS │
│           │     │           │     │           │     │           │
│ Fetch raw │     │ Raw dump  │     │ Cleaned,  │     │ Read      │
│ from APIs │     │ append-   │     │ deduped,  │     │ catalog,  │
│           │     │ only      │     │ grouped   │     │ produce   │
│           │     │           │     │ by ticker │     │ output    │
└───────────┘     └───────────┘     └───────────┘     └───────────┘
```

1. **Crawlers** fetch news from Alpaca's free News API
2. **Staging** stores raw articles in daily JSON files
3. **Catalog** deduplicates and groups articles by ticker
4. **Consumers** generate plain-English summaries via GPT-4o-mini

## Installation

```bash
# Clone the repo
git clone https://github.com/yourusername/holdup.git
cd holdup

# Install dependencies
pip install alpaca-py openai python-dotenv click

# Run setup
PYTHONPATH=src python3 -m holdup.cli setup
```

## Quick start

```bash
# Add tickers to your watchlist
holdup add AAPL MSFT NVDA

# Run the full pipeline
holdup check
```

## Commands

### Watchlist management

```bash
holdup setup              # Interactive: configure API keys
holdup add AAPL MSFT      # Add tickers to watchlist
holdup remove TSLA        # Remove a ticker
holdup list               # Show your watchlist
```

### Pipeline

```bash
holdup check              # Full pipeline for all watchlist tickers
holdup check AAPL MSFT    # Full pipeline for specific tickers only
```

### Individual stages (for debugging)

```bash
holdup crawl              # Stages 1-2: fetch and stage articles
holdup catalog            # Stage 3: build catalog from staging
holdup resummarize        # Stage 4: re-run summary on existing catalog
```

## Configuration

All data is stored in `~/.holdup/`:

```
~/.holdup/
├── .env                  # API keys (created by 'holdup setup')
├── watchlist.json        # Your tickers
├── staging/              # Raw articles by date
├── catalog/              # Cleaned articles by date
└── output/summary/       # Generated summaries
```

## API keys

You'll need:

1. **Alpaca API** (free) - [Sign up at alpaca.markets](https://alpaca.markets/)
2. **OpenAI API** - [Get key at platform.openai.com](https://platform.openai.com/)

Run `holdup setup` to configure these interactively.

## Cost

Approximately $1.50/month for 30 tickers checked daily (GPT-4o-mini pricing + Alpaca free tier).

## Running without installation

If you haven't installed the package, run commands with PYTHONPATH:

```bash
PYTHONPATH=src python3 -m holdup.cli check
```

## License

MIT
