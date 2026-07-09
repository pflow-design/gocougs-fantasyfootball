# scripts/

New build + data scripts live here.

Planned:
- A Yahoo scraper (see `LEAGUE_IDS.md` for URLs; official OAuth2 API preferred over cookie
  scraping — see `HANDOFF.md` §7).
- A validator that reconciles scraped weekly scores against official PF and W-L (the integrity
  check used throughout this project).
- A build/generate step that turns `data/*.json` into the static site.

Keep any credentials/tokens out of the repo (they are gitignored).
