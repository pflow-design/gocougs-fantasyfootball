# legacy/

Archived Cowork-era artifacts, kept for **provenance**. These generated the original report's
data and record numbers.

- `gen_h2h_2009.py` … `gen_h2h_2024.py` — per-season regular-season weekly schedules/scores
  (the cleanest per-season dataset; see `HANDOFF.md` §2 for the differing row formats).
- `h2h_all.js`, `h2h_2025.js`, `h2h_2024_2025.js` — the `h2hData` pairwise aggregates that power
  the head-to-head tool.
- `compute_h2h.py`, `gen_h2h.py`, `fix_*.py`, `rename_kyles.py` — one-off build/fix scripts.

Treat as read-only reference. Extract needed data into `data/*.json`; don't wire these into the
new build directly.
