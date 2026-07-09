# Migrating this project to Claude Code (step-by-step)

You're on Windows, and the project lives at:
`C:\Users\Owner\OneDrive\Patrick\Vibe Coding\gocougs-fantasyfootball`

Follow these in order. Commands are shown for **Windows PowerShell** (the default terminal).
Anywhere you see a path with spaces ("Vibe Coding"), keep the quotes.

---

## 0. Prerequisites (install these first)

1. **A Claude subscription** — Claude Code requires a Pro, Max, Team, or Enterprise plan (or a
   Console/API account). The free Claude.ai plan does **not** include Claude Code.
2. **Git for Windows** — https://git-scm.com/downloads/win . Installing it also gives Claude Code
   a Bash shell (recommended). Accept the defaults during install.
3. **Node.js 22 or later** — https://nodejs.org/en/download (pick the LTS if it's 22+). Needed to
   build the static site (Astro/Eleventy) and to run any npm tooling.
4. **A GitHub account** — https://github.com (free). Optionally the **GitHub CLI**
   (https://cli.github.com) to create the repo from the terminal.

Verify Node and Git after installing (open a fresh PowerShell window):

```powershell
node --version   # should print v22.x or higher
git --version
```

---

## 1. Install Claude Code

In **PowerShell**:

```powershell
irm https://claude.ai/install.ps1 | iex
```

(Native install; it auto-updates in the background. Alternatives: the **Claude Desktop app**
has a GUI Claude Code, or `npm install -g @anthropic-ai/claude-code`.)

Verify:

```powershell
claude --version
claude doctor      # deeper health check of the install
```

If `claude` isn't recognized, close and reopen PowerShell (PATH needs to refresh).

---

## 2. Open the project folder and start Claude Code

```powershell
cd "C:\Users\Owner\OneDrive\Patrick\Vibe Coding\gocougs-fantasyfootball"
claude
```

The first run opens a browser to **log in** — sign in with your Claude account. After that,
Claude Code is running in that folder and can see all the files.

> **OneDrive note:** working inside a OneDrive-synced folder is fine, but once you add
> `node_modules/` (thousands of files) OneDrive will try to sync it. It's already in
> `.gitignore`; to avoid sync churn you can either exclude `node_modules` from OneDrive backup,
> or clone/develop from a non-synced path (e.g. `C:\dev\gocougs`) and push to GitHub from there.
> Not required — just smoother.

---

## 3. Initialize the git repository

If this is your first time using git on this machine, set your identity once:

```powershell
git config --global user.name "Patrick Flower"
git config --global user.email "patrick.flower@gmail.com"
```

Then, inside the project folder:

```powershell
git init
git add -A
git status          # confirm .gitignore is working: no node_modules, .env, tokens, /public
git commit -m "Import KDP fantasy football project from Cowork"
```

The `.gitignore` already blocks build output and any secrets, so this first commit is safe.

---

## 4. Let Claude Code learn the project

Inside the `claude` session, either run the built-in initializer or prompt it directly:

```
/init
```

`/init` scans the repo and writes a `CLAUDE.md` (project memory Claude Code auto-loads each
session). Then give it the real context with a first message like:

> Read HANDOFF.md and README.md fully, then summarize the plan and the current file structure
> back to me before writing any code.

This grounds Claude Code in everything from the Cowork work (data model, record definitions,
provenance, website goals).

---

## 5. Create the GitHub repo and push

**Option A — GitHub CLI (fastest):**

```powershell
gh auth login                       # one-time browser login
gh repo create gocougs-fantasyfootball --public --source . --remote origin --push
```

**Option B — via github.com:**
1. Create a new **public** repo named `gocougs-fantasyfootball` (don't add a README/.gitignore —
   you already have them).
2. Connect and push:

```powershell
git branch -M main
git remote add origin https://github.com/<your-username>/gocougs-fantasyfootball.git
git push -u origin main
```

---

## 6. Build the site (Claude Code does the heavy lifting)

Drive it with prompts. A good sequence:

1. **Scaffold the framework**
   > Set up an Astro (or Eleventy) static site in `src/` configured for GitHub Pages. Keep the
   > build output in `public/` (already gitignored).
2. **Extract data to JSON**
   > Extract the embedded `h2hData` and the hardcoded tables from `reference/kdp_report.html`
   > and `legacy/` into `data/*.json` — one file per season plus `h2h.json`, `records.json`,
   > and `managers.json`. Match the layout in `data/README.md`.
3. **Port features**
   > Build per-season pages from `data/`, port the interactive Head-to-Head tool, and build the
   > Records & History hub (regular-season Record Book per HANDOFF.md §4, champions, Hall of
   > Team Names, veterans).
4. **Preview locally** — Claude Code will give you a dev command (e.g. `npm run dev`); open the
   localhost URL it prints and iterate.

Commit as you go (`git commit`) so each working step is saved.

---

## 7. Deploy to GitHub Pages and connect `ff.patrickflower.com`

This is the same git → GitHub → Pages → GoDaddy DNS path you already used for
`mariners.patrickflower.com`; just a new repo and the `ff` subdomain.

**7a. Generate the deploy workflow.** In Claude Code:
> Add a GitHub Actions workflow that builds the site and deploys it to GitHub Pages on every
> push to `main`, using `actions/deploy-pages`.

**7b. Turn on Pages.** github.com → **Repo → Settings → Pages → Build and deployment →
Source: GitHub Actions**.

**7c. First deploy.** Push to `main`; watch the **Actions** tab. When green, confirm it loads at
the default URL `https://<your-username>.github.io/gocougs-fantasyfootball/` before adding the
domain.

**7d. Set the custom domain in GitHub.** Settings → Pages → **Custom domain** → enter
`ff.patrickflower.com` → **Save**. GitHub adds a `CNAME` file to the repo. Also have Claude Code
drop a `CNAME` file containing `ff.patrickflower.com` into the site's static assets folder (e.g.
Astro `public/`, Eleventy passthrough) so the build never drops it:
> Add a `CNAME` file containing `ff.patrickflower.com` to the static output root.

**7e. Point GoDaddy DNS at Pages.** In GoDaddy → your domain `patrickflower.com` → **DNS →
Manage Zones / Records → Add**, create a record exactly like your `mariners` one but for `ff`:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| CNAME | `ff` | `<your-username>.github.io` | 1 Hour |

(Subdomains use a CNAME to `<username>.github.io` — note: the username host, **not** the repo
path.)

**7f. Enforce HTTPS.** Back in Settings → Pages, wait for the DNS check to pass (can take a few
minutes to an hour), then tick **Enforce HTTPS**.

**7g. Base path gotcha.** Because the custom domain serves at the **root**, set the site's base
to `/`, not `/gocougs-fantasyfootball/`, or assets/links will 404. In Astro:
`site: 'https://ff.patrickflower.com'`, `base: '/'`. In Eleventy: `pathPrefix: '/'`. Tell Claude
Code you're deploying to a root custom domain so it configures this correctly.

Live at **https://ff.patrickflower.com**.

---

## 8. Optional follow-ups

- **Data-update pipeline:** if you build the Yahoo scraper (see HANDOFF.md §7), store the Yahoo
  API token/cookies in **GitHub Actions secrets** (never in the repo) or a local `.env`
  (already gitignored). Add an `.env.example` documenting the variable names.
- **Player-stat records:** decide whether to scrape box scores to fill the remaining TBD rows or
  drop them (HANDOFF.md §4 / §9).

---

## Quick reference — the whole flow

```powershell
# one-time installs: Claude subscription, Git for Windows, Node 22+, GitHub account
irm https://claude.ai/install.ps1 | iex
cd "C:\Users\Owner\OneDrive\Patrick\Vibe Coding\gocougs-fantasyfootball"
claude                       # log in
git init; git add -A; git commit -m "Import from Cowork"
# in claude:  /init   then  "Read HANDOFF.md and README.md and summarize the plan"
gh repo create gocougs-fantasyfootball --public --source . --remote origin --push
# then: scaffold → extract data → build → add Pages workflow → enable Pages → push
# domain: Settings→Pages custom domain "ff.patrickflower.com" + GoDaddy CNAME ff → <user>.github.io
# (same as your mariners subdomain); set site base path to "/"; enforce HTTPS → https://ff.patrickflower.com
```
