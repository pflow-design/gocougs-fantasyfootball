# data/ — schema & extraction status

Clean, versioned JSON — the single source of truth for the site build. Files are
extracted from `reference/kdp_report.html` (the design source of truth) and
`legacy/` per HANDOFF.md, never re-derived by guessing.

## Files & status

| File | Status | Source | Notes |
|------|--------|--------|-------|
| `managers.json` | ✅ done | report MANAGERS map + all-time W-L table + STATUS.md | 13 managers, canonical keys, all-time **regular-season** records, naming history |
| `records.json` | ✅ done | report Record Book | Regular-season Record Book (HANDOFF §4); player-stat rows are TBD |
| `champions.json` | ⚠️ partial | STATUS/HANDOFF/report/legacy headers | `titlesByManager` complete (16); `byYear` has 5 confirmed + 2010 non-canonical; 11 years pending |
| `seasons/2025.json` | ✅ done | report + scraped_2025_2010.md | Standings, playoffs, profiles, stories, PF/PA chart, validated weekly scores |
| `seasons/2010.json` | ✅ done | scraped_2025_2010.md | STANDINGS ONLY (no weekly); 12 teams; partial manager attribution; non-canonical season |
| `h2h.json` | ✅ generated | report h2hData via `scripts/extract-h2h.mjs` | 74 pairs, 13 managers |
| `seasons/2009 + 2011–2024.json` | ✅ generated | `legacy/gen_h2h_*.py` via `scripts/build-seasons.mjs` | Regular-season standings + weekly results; W-L validated vs legacy headers (2011, 2024) |

## Conventions

- **Manager keys** are the JS keys used across all files: `Raj duncan PatrickF RyanC
  David KyleK Antony Daniel Rudee Jeremy Larson KyleP Bradley`. Display labels live
  in `managers.json` (note `Larson` → **"Robbie"**).
- **Records are regular-season only.** 2009 excluded, 2010 included (HANDOFF §4).
- **Years** are 4-digit numbers/strings; the report's `'25`-style labels are expanded.
- **Corrections applied (Patrick, 2026-07):** 2010 is a canonical season (David champion);
  David was in 2009 as `cougs4bcsbid` (old data mislabeled it Larson), "Team Malaysia" was a
  hidden one-off (Irfan), and Larson was not in 2009. The per-season files reflect these;
  the report-derived all-time aggregates in `managers.json`/`h2h.json` do NOT yet — they need
  a recompute (see `managers.json` `_meta.allTimeAggregatesCaveat`).

## Season file shape (see `seasons/2025.json`)

`year, leagueId, yahooUrl, teams, regularSeasonWeeks, playoffWeeks, champion, trophy,
standings[], playoffs{}, pfpaChart{}, teamProfiles[], stories[], weeklyScores{}`.
Earlier seasons will populate at least `standings[]` and `weeklyScores{}` from the
legacy data; profiles/stories/chart are 2025-only unless authored later.

## Regenerating

- `h2h.json`: `node scripts/extract-h2h.mjs` (deterministic, exact).
- Validation gate for any weekly data (HANDOFF §5): summing a team's weekly actuals
  must reproduce its official PF and W-L. 2025 passes exactly.
