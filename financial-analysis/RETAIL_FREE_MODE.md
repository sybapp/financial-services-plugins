# Retail Free Data Mode

This mode is for individual investors who do not have enterprise data subscriptions.

## What this changes

- Uses free or low-cost data sources as the default path
- Keeps institutional sources optional (if you later get access)
- Preserves the same modeling workflows (comps, DCF, earnings)

## Quick setup

1. Back up the current connector config:

```bash
cp financial-analysis/.mcp.json financial-analysis/.mcp.paid.backup.json
```

2. Start from the retail template:

```bash
cp financial-analysis/.mcp.retail.example.json financial-analysis/.mcp.json
```

3. Replace placeholder API keys in `financial-analysis/.mcp.json` (see registration links below).

## Suggested free stack

| Source | What it covers | API key | Free tier limits |
|--------|---------------|---------|-----------------|
| SEC EDGAR | Filings, financial statements, XBRL | None (set a User-Agent) | Unlimited (10 req/s) |
| Twelve Data | Real-time & historical market data | [Register](https://twelvedata.com/register) | 800 req/day, 8 per minute |
| FRED | Macro, rates, inflation, labor series | [Register](https://fred.stlouisfed.org/docs/api/api_key.html) | Unlimited |
| Alpha Vantage | Prices, fundamentals, technicals | [Register](https://www.alphavantage.co/support/#api-key) | 25 req/day |
| Yahoo Finance / company IR | Estimate cross-checks, transcripts | None (web) | N/A |

**Prerequisites:**
- Node.js 18+ (for `npx`-based MCP servers)
- Docker (required only for the SEC EDGAR MCP server; if Docker is unavailable, use the SEC EDGAR XBRL API directly via web fetch)

## Capability gaps vs paid terminals

- Consensus depth: usually lighter than FactSet/Bloomberg/IBES
- Fixed income analytics: no full YieldBook-style curve/risk stack
- Private markets: no full PitchBook/CapIQ private-company coverage

## Working rules

- Prefer primary sources first (SEC filings, company IR)
- For each critical metric, cross-check with at least one second source
- Add source + date notes for every hardcoded input
- If a free source is delayed or missing, flag confidence explicitly
