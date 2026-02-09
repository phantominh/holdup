"""Configuration management for holdup."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv


def get_holdup_dir() -> Path:
    """Get the holdup data directory (~/.holdup/)."""
    return Path.home() / ".holdup"


def get_env_path() -> Path:
    """Get the path to the .env file."""
    return get_holdup_dir() / ".env"


def get_watchlist_path() -> Path:
    """Get the path to the watchlist.json file."""
    return get_holdup_dir() / "watchlist.json"


def get_staging_dir() -> Path:
    """Get the staging directory path."""
    return get_holdup_dir() / "staging"


def get_catalog_dir() -> Path:
    """Get the catalog directory path."""
    return get_holdup_dir() / "catalog"


def get_output_dir() -> Path:
    """Get the output directory path."""
    return get_holdup_dir() / "output"


def ensure_directories() -> None:
    """Create all necessary directories if they don't exist."""
    dirs = [
        get_holdup_dir(),
        get_staging_dir(),
        get_catalog_dir(),
        get_output_dir(),
        get_output_dir() / "summary",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def load_env() -> None:
    """Load environment variables from ~/.holdup/.env."""
    env_path = get_env_path()
    if env_path.exists():
        load_dotenv(env_path)


def get_alpaca_credentials() -> tuple[str, str]:
    """Get Alpaca API credentials from environment."""
    load_env()
    api_key = os.getenv("ALPACA_API_KEY", "")
    api_secret = os.getenv("ALPACA_API_SECRET", "")
    return api_key, api_secret


def get_openai_api_key() -> str:
    """Get OpenAI API key from environment."""
    load_env()
    return os.getenv("OPENAI_API_KEY", "")


def load_watchlist() -> list[str]:
    """Load the watchlist from ~/.holdup/watchlist.json."""
    watchlist_path = get_watchlist_path()
    if not watchlist_path.exists():
        return []
    with open(watchlist_path, "r") as f:
        return json.load(f)


def save_watchlist(tickers: list[str]) -> None:
    """Save the watchlist to ~/.holdup/watchlist.json."""
    ensure_directories()
    watchlist_path = get_watchlist_path()
    # Normalize to uppercase and remove duplicates while preserving order
    seen = set()
    normalized = []
    for t in tickers:
        upper = t.upper()
        if upper not in seen:
            seen.add(upper)
            normalized.append(upper)
    with open(watchlist_path, "w") as f:
        json.dump(normalized, f, indent=2)


def add_tickers(tickers: list[str]) -> list[str]:
    """Add tickers to the watchlist. Returns the updated watchlist."""
    current = load_watchlist()
    current_set = set(current)
    for t in tickers:
        upper = t.upper()
        if upper not in current_set:
            current.append(upper)
            current_set.add(upper)
    save_watchlist(current)
    return current


def remove_ticker(ticker: str) -> bool:
    """Remove a ticker from the watchlist. Returns True if removed."""
    current = load_watchlist()
    upper = ticker.upper()
    if upper in current:
        current.remove(upper)
        save_watchlist(current)
        return True
    return False


def save_env(alpaca_key: str, alpaca_secret: str, openai_key: str) -> None:
    """Save API keys to ~/.holdup/.env."""
    ensure_directories()
    env_path = get_env_path()
    content = f"""# Alpaca API credentials
ALPACA_API_KEY={alpaca_key}
ALPACA_API_SECRET={alpaca_secret}

# OpenAI API key
OPENAI_API_KEY={openai_key}
"""
    with open(env_path, "w") as f:
        f.write(content)
    # Set restrictive permissions on .env file
    env_path.chmod(0o600)
