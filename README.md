# KDP "Go Cougs" Fantasy Football

A history site for the KDP fantasy football league — 16 seasons (2009–2025) of standings,
records, head-to-head history, champions, and lore. Being built into a **published, public,
multi-page website** hosted on **GitHub Pages** at **https://ff.patrickflower.com**.

> **Start here → [`HANDOFF.md`](HANDOFF.md)** — the full project brief (data model, every
> decision made, provenance, website plan, and architecture options). Read it before building.
>
> **Moving to Claude Code? → [`MIGRATION.md`](MIGRATION.md)** — detailed step-by-step setup,
> from installing Claude Code to deploying on GitHub Pages.

## Status

Migrating from a single-file Cowork report (`reference/kdp_report.html`) to a data-driven
static site. The data and all record definitions are settled; the site build is the next step.

## Repo structure

```
.
├── README.md              ← you are here
├── HANDOFF.md             ← START HERE: full handoff brief
├── LEAGUE_IDS.md          ← Yahoo league ID + URL for every season 2009–2026
├── STATUS.md              ← original project status / manager-naming reconciliation
├── scraped_2025_2010.md   ← raw scraped weekly data + records for 2025 & 2010
│
├── data/                  ← clean JSON data (to be extracted from legacy/ + reference/)
├── src/                   ← site source: templates, components, styles (new build)
├── scripts/               ← scrapers + build/generate scripts (new)
├── public/                ← build output for GitHub Pages (gitignored)
│
├── reference/             ← design source of truth: the original single-page report
└── legacy/                ← archived Cowork-era generators & data (provenance; do not run blindly)
```

## Quick start (for Claude Code)

1. Read [`HANDOFF.md`](HANDOFF.md) end to end.
2. Extract the data: pull the `h2hData` object and hardcoded tables out of
   `reference/kdp_report.html` and the `legacy/*.js` / `legacy/gen_h2h_*.py` files into
   `data/*.json` (one file per season + an all-time/records file + the H2H aggregates).
3. Build multi-page site in `src/` (Astro or Eleventy recommended; plain HTML/JS also fine),
   port the interactive H2H tool and the Record Book, generate per-season pages from `data/`.
4. Wire a GitHub Actions workflow to build and deploy to Pages.

## Data & provenance

Scores were scraped from Yahoo Fantasy (see `LEAGUE_IDS.md` for URLs) and validated by summing
weekly scores back to official PF and W-L. Records are **regular-season only**; see `HANDOFF.md`
§4 for the exact definitions and the 2009-excluded / 2010-included decisions.

Data is non-sensitive (fantasy scores) and safe to publish. **Never commit Yahoo API tokens or
session cookies** — see `.gitignore`.
