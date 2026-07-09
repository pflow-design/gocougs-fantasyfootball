# KDP "Go Cougs" Fantasy Football — Project Handoff

**Purpose of this document:** hand this project off from Cowork to **Claude Code** to build a
full, published, **public website** for the league. It captures the current state, the data
model, every substantive decision made so far, how the data was gathered and validated, the
known gaps, and the requirements + architecture options for the website.

**Read these companion files too:**
- `STATUS.md` — original project status / manager-naming reconciliation
- `LEAGUE_IDS.md` — Yahoo league ID + URL pattern for every season 2009–2026
- `scraped_2025_2010.md` — raw scraped weekly data + computed records for 2025 and 2010

---

## 1. Goal

Turn the existing single-file report (`kdp_report.html`) into a **published, public,
multi-page website** for the league's friends, hosted on **GitHub Pages** at the custom domain
**https://ff.patrickflower.com**. Desired features:

1. **Multi-page, per-season** — a landing page plus a page per season (2009–2025) with
   standings, results, playoff bracket, team profiles, and season stories.
2. **Interactive Head-to-Head tool** — pick any two managers, see full all-time H2H history
   (already prototyped in the current report's lower section).
3. **Records & history hub** — all-time Record Book, champions timeline, "Hall of Team Names,"
   and league lore/veterans.

Tone of the league is irreverent/jokey (see commissioner notes in Yahoo) — the site can lean
into that personality.

---

## 2. Current state — what exists today

`kdp_report.html` (≈1,120 lines, self-contained, no external dependencies) is a complete,
working single-page report covering 2009–2025. It already contains, as hardcoded HTML plus a
little inline JS/SVG:

- 2025 Final Standings, PF/PA SVG bar chart (inline SVG — Chart.js was removed because it
  failed under the `file://` protocol), 2025 Playoff bracket, 2025 team profiles, season stories
- Season-by-season + all-time W-L table (sortable)
- **All-Time Head-to-Head Comparison** — interactive dropdown tool driven by a `h2hData` JS
  object embedded at the bottom of the HTML
- **All-Time Record Book — Regular Season** (recently overhauled; see §4)
- League Veterans, Hall of Team Names

The report opens in any browser with no server. All data is embedded inline.

### Data assets (the "source of truth" behind the report)
- `h2h_all.js`, `h2h_2025.js`, `h2h_2024_2025.js` — the `h2hData` object: **pairwise career
  head-to-head aggregates** across all managers (wins, PF, biggest game, last meeting, playoff
  appearances, seasons). This powers the interactive H2H tool. NOTE: aggregates, not weekly.
- `gen_h2h_2009.py` … `gen_h2h_2024.py` — per-season generators. Each holds that season's
  **regular-season weekly schedule + scores** as a Python dict (`SCHED_YYYY`), with playoffs
  stored separately (`PLAYOFFS_YYYY`). These built the `h2hData`. **This is the closest thing
  to a clean per-season weekly dataset** and is what the record recomputation used.
  - Format note: 2011–2023 use `SCHED_YYYY = {mgr: [(wk, oppKey, ownScore, oppScore), ...]}`.
  - 2024 uses per-team list variables assembled into `SCHED_2024`, rows are
    `[wk, oppTeamName, 'Win'/'Loss', ownScore, oppScore]`.
  - 2009 uses `GAMES_2009 = [(wk, mgrA, mgrB, scoreA, scoreB, is_playoff), ...]`.
- `gen_h2h.py`, `compute_h2h.py`, `fix_report.py`, `fix_2019_larson.py`, `rename_kyles.py` —
  one-off build/fix scripts (historical; document only).
- `scraped_2025_2010.md` — NEW: full 2025 weekly scores (League 205492) and 2010 team-season
  data (League 264678), both validated. 2010 was previously missing entirely.

### Data gaps
- **Weekly player-level stats do not exist anywhere in the project** (only team match scores).
  So player-stat records (TDs, rushing/receiving/passing yards) cannot be recomputed — see §5.
- The `h2hData` aggregates likely include playoff games; the `SCHED_YYYY` dicts are
  regular-season only. Use `SCHED_YYYY` (and the scraped files) for regular-season truth.

---

## 3. Data model & conventions

### Managers (canonical names) and naming history
From `STATUS.md`, reconciled against Yahoo and confirmed by Patrick:

| JS key | Display | KDP since | Notes |
|--------|---------|-----------|-------|
| Raj | Raj | '09 | |
| duncan | Duncan | '09 | Commissioner |
| PatrickF | Patrick | '09 | (the owner / you) |
| RyanC | Ryan C | '09 | distinct from "Rudee"; missing 2011 attribution |
| David | David | '09 | scmid 2 in 2009 WaZZU ("Team Malaysia") |
| KyleK | Kyle K | '09 | formerly "Kyle" |
| Antony | Antony | '09 | absent 2019–2021 |
| Daniel | Daniel | '09 | |
| Larson | Larson | '09 | alumni / historical |
| Bradley | Bradley | '09 | alumni |
| KyleP | Kyle P | '12 | formerly "Kyle2"; last active 2021 |
| Rudee | Rudee | '19 | was mislabeled "Ryan" (rmath23@hotmail.com) in early builds |
| Jeremy | Jeremy Trevino | '20 | 2025 & 2023 champion |

**Gotchas:** "Ryan" in older scripts = **Rudee**, not Ryan C. "Kyle"→Kyle K, "Kyle2"→Kyle P.
Some seasons have "hidden" (departed) managers with no recoverable names.

### Season structure (regular-season week ranges — important for records)
- 2009: 10 teams, **weeks 1–13** reg (WaZZU league, ID 320012)
- 2010: **12 teams, weeks 1–13** reg (ID 264678) — larger era with several one-off managers
  (DJ, Brad, etc.), some abandoned teams
- 2011–2020: 10 teams, **weeks 1–14** reg
- 2021–2025: 10 teams, **weeks 1–15** reg (playoffs weeks 16–17)

### League IDs / Yahoo URLs
Full list in `LEAGUE_IDS.md`. Pattern for any past season:
`https://football.fantasysports.yahoo.com/<YEAR>/f1/<LEAGUE_ID>` ; weekly matchups add
`?matchup_week=<N>&module=matchups&lhst=matchups`. The bare `/f1/<id>` only resolves the
current season. 2026 (107782) is the auto-renewed pre-draft shell.

---

## 4. Record Book overhaul — decisions made (READ BEFORE TOUCHING RECORDS)

The "All-Time Record Book" was reworked from a first-pass version that had placeholders
("[Mgr TBD]") and mixed playoff/regular-season numbers. Final agreed definitions and choices:

- **Two rows per metric:** the `2025` row = **that current season's** leader; the `All Time`
  row = the best/worst mark **across all seasons**. (Originally the label read "Season," which
  was ambiguous; it was renamed to the explicit year "2025".)
- **Regular season only.** Playoff games are excluded from every record. The section title is
  "All-Time Record Book — Regular Season" with an italic note stating this.
- **2009: EXCLUDED** from records (10-team WaZZU era, much lower scoring, not comparable).
- **2010: INCLUDED** (user decision), even though it's a 12-team era with departed managers.
  Consequence: the all-time **Low Single Week** is now "Too Good, '10 — 22.36" (an abandoned
  team; manager is hidden, so the team name is shown).
- **Schedule strength** = average opponent points scored against a manager (i.e., Points-Against
  ÷ games). 2025 schedule figures were computed from the standings PA column.
- **Win-streak all-time = 9**, shown as "Duncan, '21" but actually a multi-way tie
  (Raj '11, Raj '18, Duncan '21, and a 2010 team). Displayed as a single holder for now.

### Confirmed regular-season record holders (current values in the report)
- Most Wins: 2025 = Rudee & David 11 · All-Time = David '20, 13
- Win Streak: 2025 = David 7 · All-Time = Duncan '21, 9 (tie)
- Most Losses: 2025 = Duncan 12 · All-Time = Patrick '21, 13
- Loss Streak: 2025 = Kyle K/Raj 7 · All-Time = Patrick '21, 12
- Biggest Blowout: 2025 = Patrick vs Daniel 70.28 (Wk7) · All-Time = Kyle K vs David '23, 100.58
- Closest Game: 2025 = Ryan C vs Duncan 0.02 (Wk14) · All-Time = same, '25, 0.02
- Hardest Schedule: 2025 = Patrick 122.28/wk · All-Time = Antony '18, 137.63/wk
- Easiest Schedule: 2025 = Antony 108.93/wk · All-Time = Patrick '12, 97.02/wk
- High Single Week: 2025 = Rudee 169.80 (Wk15) · All-Time = Kyle K '14, 196.20
- High Season Total: 2025 = David 1,900.36 · All-Time = Rudee '21, 1,989.20
- Low Single Week: 2025 = Kyle K 54.08 (Wk8) · All-Time = Too Good '10, 22.36
- Low Season Total: 2025 = Duncan 1,534.66

### Still TBD (intentionally left blank — data does not exist in project)
The all-time **player-stat** rows — Most TDs, Rush Yds, Rec Yds, Pass Yds (weekly), and
Low Season Avg (offense) — are marked "TBD". They require per-player weekly box scores across
all 16 seasons (~2,000 Yahoo pages) and were deliberately deferred.

---

## 5. How the recent data was gathered & validated (provenance)

- 2025 & 2010 weekly scores were scraped from Yahoo (user logged into Chrome) via the
  authenticated matchup pages, using the `<YEAR>/f1/<ID>?matchup_week=N&module=matchups`
  pattern. On each matchup, the FIRST score shown is the actual, the second is projected.
- **Validation method (reuse this):** sum each team's weekly actual scores and compare to the
  official standings PF, and recompute W-L. For 2025, all 10 teams matched PF and W-L exactly;
  for 2010, team-season totals matched standings. This is the integrity check for any re-scrape.
- Record recomputation script logic lived in throwaway Python (loading `SCHED_YYYY` dicts +
  2009 `GAMES_2009` + scraped 2025/2010). If rebuilding, regenerate clean per-season JSON first.

---

## 6. Website requirements (agreed)

- **Host:** GitHub Pages (static hosting only — no server-side code at runtime), served at the
  custom domain **ff.patrickflower.com** (GoDaddy CNAME → GitHub Pages; see `MIGRATION.md` §7).
  Because it serves at the domain root, set the site base path to `/`.
- **Structure:** multi-page. Landing/home + one page per season (2009–2025) + a Records/History
  hub + an interactive H2H tool page.
- **Interactive H2H:** port and expand the existing dropdown tool; it runs entirely client-side
  off a `h2hData` JSON blob, so it fits static hosting perfectly.
- **Records hub:** the Record Book (regular-season, per §4), champions timeline, Hall of Team
  Names, veterans/lore.
- **Public:** no secrets in the repo. Data is non-sensitive (fantasy scores) — safe to publish.

### Suggested architecture for Claude Code (not binding)
- A **data-driven static build**: put clean data in `/data/*.json` (one file per season + an
  all-time/records file + the H2H aggregates), and generate pages with a lightweight static-site
  generator (**Astro** or **Eleventy** are good fits for GitHub Pages; both output plain static
  files and support components + per-season page templates from data). Plain HTML/CSS/JS is also
  viable given the current report is already self-contained.
- Reuse the current report's inline SVG chart approach (no CDN dependency needed) or a small
  charting lib bundled locally.
- Deploy via a **GitHub Actions** workflow that builds and pushes to Pages (`actions/deploy-pages`).

### Migration steps to Claude Code
1. `git init` the project folder; add a `.gitignore` (exclude any future secrets/token files).
2. Restructure: `/data` (JSON), `/src` (templates/components), `/scripts` (scrapers/build),
   `/public` or build output. Move `kdp_report.html` to `/reference` as the design source.
3. Extract the embedded `h2hData` and hardcoded tables into `/data/*.json`.
4. Build pages from data; port the H2H tool and Record Book.
5. Add the Pages deploy workflow; publish.

---

## 7. Static snapshot vs. repeatable pipeline (requested tradeoff analysis)

**The core constraint:** GitHub Pages serves **static files only** — it cannot run a scraper at
request time. "Keeping data current" therefore always means *regenerating static files*, the
only question is how automated that regeneration is. Yahoo private-league data also **requires
authentication**, which shapes everything below.

### Option A — Static snapshot
- **What it is:** build the site once from the data you have (frozen through 2025). When a season
  ends, a human re-scrapes and rebuilds by hand, commits, and redeploys.
- **Requirements:** essentially none beyond the site itself + a git repo. No credentials stored,
  no scheduled jobs, no API registration.
- **Pros:** simplest; zero standing infrastructure; nothing to break between updates; no secrets
  anywhere (safest for a public repo); fully within GitHub Pages' free static model.
- **Cons:** each yearly update is manual and depends on a logged-in Yahoo session; easy to let
  data drift; the scraping know-how must be re-followed each time (mitigated by this doc +
  `LEAGUE_IDS.md`).
- **Best when:** the site updates ~once per season and a manual annual rebuild is acceptable
  (very likely the right call for a league history site).
- **Effort:** low.

### Option B — Repeatable pipeline
- **What it is:** a documented, scripted flow — pull each season's data → write clean JSON →
  rebuild the static site with one command (or on a schedule) → deploy.
- **Requirements / considerations:**
  - **Auth to Yahoo.** Two paths: (1) the official **Yahoo Fantasy Sports API** (OAuth2 — register
    an app, handle access/refresh tokens that expire and must be refreshed); or (2) **authenticated
    scraping** using session cookies (brittle, breaks on Yahoo UI/login changes, and arguably
    against ToS). The API is the durable choice but adds OAuth plumbing.
  - **Secret management.** Tokens/cookies must **never** be committed to a public repo. If
    automating via GitHub Actions, store them in **Actions secrets**; if running locally, keep them
    in an ignored `.env`. Token refresh has to be handled (Yahoo tokens are short-lived).
  - **Where it runs.** Pages can't run it; the pipeline runs **locally** or in **GitHub Actions**
    (scheduled/`workflow_dispatch`), regenerates the static files, and commits/deploys them.
  - **Validation gate.** Bake in the PF/W-L reconciliation check (see §5) so a bad scrape can't
    silently publish wrong numbers.
  - **Rate limits / resilience.** Be gentle with requests; handle partial failures and re-runs.
- **Pros:** adding a new season (or correcting data) is one command; reduces human error; enables
  future automation (e.g., weekly in-season updates).
- **Cons:** meaningfully more upfront engineering; ongoing token maintenance; more moving parts
  and failure modes; OAuth app registration overhead.
- **Best when:** you expect to update frequently, want in-season refreshes, or want anyone (not
  just you) to be able to trigger an update.
- **Effort:** medium-high.

### Recommendation (for the doc, not a decision)
A **hybrid** fits this project best: ship the **static site** to Pages now (Option A output), and
**scaffold a semi-automated local rebuild script** (Option B-lite) that you run after each season
with your Yahoo login — reusing the scrape pattern + validation already proven here. Full
automation (Actions + Yahoo OAuth) is worthwhile **only if** you later want hands-off in-season
updates. Either way, keep the **build static and the data in versioned JSON**, so upgrading from
snapshot → pipeline later doesn't require rearchitecting the site.

---

## 8. Session history (what was done in Cowork, chronologically)

1. Investigated the Record Book's "[Mgr TBD]" placeholders — found they were hardcoded, not
   generated.
2. Corrected "Most Wins All-Time" attribution (David, 2020) and clarified 2025 vs all-time.
3. Discovered the "Season" column really meant "the 2025 season (incl. playoffs)"; **relabeled
   it "2025"** for clarity while keeping the logic.
4. Decision: **make the whole Record Book regular-season only**; recomputed every computable
   record from `SCHED_YYYY` (2011–2024) + 2009 `GAMES_2009`; corrected several playoff-inflated
   values; marked non-computable cells TBD; updated the title.
5. Chose to **exclude 2009** from records; filled placeholders one at a time with verification.
6. Found **2010 was missing entirely** and several 2025 cells needed weekly data.
7. Located all season **league IDs** (saved to `LEAGUE_IDS.md`) after discovering the
   `<YEAR>/f1/<ID>` archive URL pattern.
8. **Scraped 2025** (League 205492, Weeks 1–15) and **2010** (League 264678, Weeks 1–13) via the
   authenticated browser; validated both against official PF/W-L; saved to `scraped_2025_2010.md`.
9. Filled the five 2025 Record Book cells; **included 2010** (Low Single Week → Too Good '10,
   22.36); left player-stat rows as **TBD** by choice.

---

## 9. Open questions for the website build
- ~~Custom domain vs `*.github.io`?~~ Decided: **ff.patrickflower.com** (GoDaddy CNAME → Pages).
- Final data-update approach (snapshot vs pipeline — see §7).
- Whether to resolve the player-stat TBDs (needs box-score scraping) or drop those rows.
- Whether to display the win-streak record as an explicit multi-way tie.
- Visual direction / branding for the public site (the league's humor can inform it).
