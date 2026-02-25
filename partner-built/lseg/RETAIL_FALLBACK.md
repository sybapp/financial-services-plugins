# LSEG Plugin: Retail Fallback Guide

Use this guide if you do not have LSEG entitlements.

## What you can and cannot replace

- You can replace parts of equity/macro workflows with free/public data.
- You cannot fully replace YieldBook-grade fixed income analytics, full vol surfaces, or OTC swap analytics with free sources.

## Command-by-command fallback

### `/macro-rates`

- Replace with FRED series via `fred-mcp-server`:
  - Treasury yields: `DGS1`, `DGS2`, `DGS5`, `DGS10`, `DGS30` (daily constant maturity)
  - Yield curve spread: `T10Y2Y` (10Y minus 2Y), `T10Y3M` (10Y minus 3M)
  - Inflation: `CPIAUCSL` (CPI), `PCEPILFE` (core PCE), `T5YIE` / `T10YIE` (breakeven inflation)
  - Labor: `UNRATE` (unemployment), `PAYEMS` (nonfarm payrolls)
  - GDP: `GDP`, `GDPC1` (real GDP)
  - Fed funds: `FEDFUNDS`, `DFEDTARU` / `DFEDTARL` (target range)
- Output style can stay similar: curve shape, inflation trend, policy context.

### `/research-equity`

- Fundamentals: SEC EDGAR filings and company IR materials.
- Prices/returns: Twelve Data, Yahoo Finance, Alpha Vantage.
- Consensus: Yahoo Finance or other free/public sources.

### `/analyze-swap-curve`

- Approximate with Treasury curve analysis using FRED series (`DGS1` through `DGS30`).
- For swap spread context, compare Treasury yields against `BAMLC0A0CM` (ICE BofA corporate index OAS) from FRED.
- Note explicitly that this is a proxy, not true OTC swap pricing.

### `/analyze-option-vol`

- Use public options-chain snapshots and historical realized volatility.
- Note that full institutional implied-vol surface analytics may be unavailable.

### `/analyze-fx-carry`

- Use Twelve Data or Alpha Vantage for spot FX rates.
- For interest rate differentials, use FRED central bank policy rate series (e.g., `FEDFUNDS`, `ECBDFR`, `IRSTCB01JPM156N`).
- Keep analysis qualitative if forward curve granularity is limited.

### `/analyze-bond-rv`, `/review-fi-portfolio`, `/analyze-bond-basis`

- Use FRED credit spread series for relative value context:
  - Investment grade OAS: `BAMLC0A0CM`
  - High yield OAS: `BAMLH0A0HYM2`
  - BBB spread: `BAMLC0A4CBBB`
- Flag confidence as lower when OAS, key-rate duration, CTD analytics, or scenario engines are unavailable.

## Recommended setup

- Enable `financial-analysis/.mcp.json` retail mode.
- Prefer SEC + FRED + free market APIs first.
- Add source/date notes to every hardcoded input.
