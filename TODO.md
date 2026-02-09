# holdup - Future Plans

## 1. More Data Sources

Add crawlers for:
- **Reddit** - r/wallstreetbets, r/stocks (use PRAW library)
- **SEC Filings** - Company reports via EDGAR API
- **Yahoo Finance** - Backup news source

## 2. Editable Prompts

Create `prompts.yaml` so users can:
- Edit the summary prompt without touching code
- Add different styles (short, detailed)

## 3. Make It an Agent

**Goal:** Let the AI decide what to do, not just follow a script.

Current flow (pipeline):
```
User runs command → Fetch all tickers → Summarize all → Done
```

Agent flow:
```
User asks question → AI picks what data to fetch → AI decides if it needs more → AI answers
```

**What we need to add:**
1. Let the AI call our crawlers as "tools" (OpenAI function calling)
2. Give it a loop: think → act → observe → repeat
3. Add memory so it remembers past conversations

**Simplest first step:**
Make a `holdup ask "why did NVDA drop?"` command that lets GPT decide which tickers to look up.
