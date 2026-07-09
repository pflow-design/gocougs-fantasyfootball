# data/ — schema & extraction status

Clean, versioned JSON — the single source of truth for the site build. Files are
extracted from `reference/kdp_report.html` (the design source of truth) and
`legacy/` per HANDOFF.md, never re-derived by guessing.

## Files & status

| File | Status | Source | Notes |
|------|--------|--------|-------|
| `managers.json` | ✅ recomputed | `data/seasons/*.json` + `champions.json` via `scripts/recompute.mjs` | 13 managers, all-time **regular-season** records (17 seasons), naming history |
| `records.json` | ✅ done | report Record Book | Regular-season Record Book (HANDOFF §4); player-stat rows are TBD |
| `champions.json` | ✅ complete | legacy `gen_h2h_*.py` headers + docs | All 17 champions; `titlesByManager` sums to 17 (David 2 = 2010 + 2020) |
| `seasons/2025.json` | ✅ done | report + scraped_2025_2010.md | Standings, playoffs, profiles, stories, PF/PA chart, validated weekly scores |
| `seasons/2010.json` | ✅ done | scraped_2025_2010.md | STANDINGS ONLY (no weekly); 12 teams; partial manager attribution |
| `h2h.json` | ✅ recomputed | `data/seasons/*.json` + legacy playoffs via `scripts/recompute.mjs` | 74 pairs, 13 managers; incl. playoff games |
| `seasons/2009 + 2011–2024.json` | ✅ generated | `legacy/gen_h2h_*.py` via `scripts/build-seasons.mjs` | Regular-season standings + weekly results; W-L validated vs legacy headers |

## Conventions

- **Manager keys** are the JS keys used across all files: `Raj duncan PatrickF RyanC
  David KyleK Antony Daniel Rudee Jeremy Larson KyleP Bradley`. Display labels live
  in `managers.json` (note `Larson` → **"Robbie"**).
- **Records are regular-season only.** 2009 excluded, 2010 included (HANDOFF §4).
- **Years** are 4-digit numbers/strings; the report's `'25`-style labels are expanded.
- **Corrections applied (Patrick, 2026-07), reflected everywhere incl. the recomputed
  aggregates:** (1) 2010 is canonical (David champion); (2) David was in 2009 as `cougs4bcsbid`
  (old data mislabeled it Larson), "Team Malaysia" was a hidden one-off (Irfan), Larson absent
  2009; (3) the 2019 hidden 4-10 team mislabeled `Antony` in `SCHED_2019` is actually Larson —
  Antony was absent 2019. `managers.json` + `h2h.json` are recomputed from the corrected season
  data (`scripts/recompute.mjs`); validated: all 52 H2H pairs not touched by these corrections
  match the old report exactly.

## Season file shape (see `seasons/2025.json`)

`year, leagueId, yahooUrl, teams, regularSeasonWeeks, playoffWeeks, champion, trophy,
standings[], playoffs{}, pfpaChart{}, teamProfiles[], stories[], weeklyScores{}`.
Earlier seasons will populate at least `standings[]` and `weeklyScores{}` from the
legacy data; profiles/stories/chart are 2025-only unless authored later.

## Regenerating

Order matters — seasons first, then the aggregates that derive from them:
1. `node scripts/build-seasons.mjs` — rebuilds `seasons/2009 + 2011–2024.json` from `legacy/`.
2. `node scripts/recompute.mjs` — validate-only diff vs current `managers.json`/`h2h.json`.
3. `node scripts/recompute.mjs --write` — writes the recomputed `managers.json` + `h2h.json`.

`scripts/extract-h2h.mjs` is the older report-based H2H extractor, kept for provenance;
`recompute.mjs` (season-derived) is now authoritative.

Validation gate for any weekly data (HANDOFF §5): summing a team's weekly actuals must
reproduce its official PF and W-L. 2025 passes exactly; `recompute.mjs` also checks that
correction-free H2H pairs still match the original report.
