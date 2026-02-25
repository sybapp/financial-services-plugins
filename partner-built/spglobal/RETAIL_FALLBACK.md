# S&P Global Plugin: Retail Fallback Guide

Use this guide if you do not have Capital IQ / Kensho API access.

## What you can and cannot replace

- You can reproduce core public-company workflows with SEC filings, company IR, and free market data providers.
- You cannot fully replicate proprietary private-company coverage, deep ownership datasets, or institutional consensus depth.

## Skill-by-skill fallback

### Tear Sheets

- Company profile and financial snapshot: SEC 10-K/10-Q (EDGAR full-text search or XBRL API) + company IR + Yahoo Finance.
- Price/performance and valuation checks: Twelve Data or Alpha Vantage for historical prices; Yahoo Finance for current multiples (P/E, EV/EBITDA).
- Ownership/holder detail: SEC Schedule 13D/13G and DEF 14A proxy filings for major holders.

### Industry Transaction Summaries

- Source deals from SEC 8-K/S-4 filings, company press releases, and reliable financial news archives.
- For deal multiples, extract from merger proxy statements (DEFM14A) on EDGAR — these contain disclosed EV, revenue, and EBITDA at time of deal.
- Build compact transaction tables manually with explicit source/date citations.

### Earnings Previews

- Consensus: Yahoo Finance or other free/public sources.
- Guidance and key watch items: prior quarter earnings release, transcript, and IR deck.
- Always label estimate source and timestamp ("as of" date).

### Funding Digest / Private-Market Style Workflows

- Use publicly reported rounds from company releases and major tech/business outlets.
- Coverage will be partial relative to institutional private-market databases.

## Recommended operating rules

- Prioritize primary documents (SEC + company IR).
- Cross-check critical numbers with at least one additional source.
- Add clear source/date citations for every hardcoded value.
- If data is missing, state limitation explicitly instead of inferring.
