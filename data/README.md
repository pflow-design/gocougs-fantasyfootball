# data/

Clean, versioned JSON — the single source of truth for the site build.

Suggested layout (to be created during migration):
- `seasons/2009.json` … `seasons/2025.json` — per-season standings, weekly results, playoffs,
  team profiles, stories.
- `h2h.json` — the pairwise all-time head-to-head aggregates (extracted from `legacy/h2h_all.js`).
- `records.json` — the all-time Record Book (regular-season; see `HANDOFF.md` §4).
- `managers.json` — canonical manager names + naming history (from `STATUS.md`).

Extract these from `reference/kdp_report.html` and `legacy/` rather than re-deriving.
