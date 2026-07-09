#!/usr/bin/env python3
"""
gen_h2h_2009.py — Merge 2009 WaZZU (ID: 320012) matchup data into h2hData.

Managers in 2009 WaZZU:
  scmid 1  → Larson   (cougs4bcsbid, hidden)
  scmid 2  → David    (Team Malaysia, display name "Irfan Since '05") ← ASSUMPTION — confirm with Patrick
  scmid 3  → Bradley  (FUCK YOU RUDEE)
  scmid 4  → RyanC    (Purple Reign, "Ryan C Since '06")
  scmid 5  → Raj      (Sound Records)
  scmid 6  → Daniel   (Favre and Away)
  scmid 7  → PatrickF (AIDS)
  scmid 8  → Kyle     (Ballcuzzis)
  scmid 9  → duncan   (The Frying Pans) ← 2009 CHAMPION
  scmid 10 → Antony   (The Blackouts)

Season structure:
  Regular season: weeks 1–13, 5 games/wk = 65 games
  Playoffs: 6-team bracket (seeds 1&2 got week-14 byes), weeks 14–16 = 7 games
  Total: 72 games

Final standings: 1 duncan, 2 Antony, 3 RyanC, 4 Kyle,
                 5 Daniel, 6 Larson, 7 David, 8 Bradley, 9 Raj, 10 PatrickF
"""

import re, pathlib

HTML = pathlib.Path(__file__).parent / 'kdp_report.html'

# ---------------------------------------------------------------------------
# 2009 games: (week, mgr_a, mgr_b, score_a, score_b, is_playoff)
# ---------------------------------------------------------------------------
GAMES_2009 = [
    # ── Week 1 ──
    (1, 'Larson',   'David',   61.22,  58.56, False),
    (1, 'Bradley',  'Antony',  97.78,  71.47, False),
    (1, 'RyanC',    'Kyle',    91.23,  85.86, False),
    (1, 'PatrickF', 'Raj',    117.95,  62.11, False),
    (1, 'Daniel',   'duncan', 148.49,  84.19, False),
    # ── Week 2 ──
    (2, 'David',    'duncan', 110.25,  72.52, False),
    (2, 'Kyle',     'Raj',    136.34,  74.79, False),
    (2, 'Antony',   'RyanC',  115.83,  73.28, False),
    (2, 'Larson',   'Bradley', 88.81,  76.02, False),
    (2, 'PatrickF', 'Daniel', 102.77,  43.57, False),
    # ── Week 3 ──
    (3, 'RyanC',    'Larson',  84.59,  58.52, False),
    (3, 'David',    'Bradley', 78.93,  77.95, False),
    (3, 'Antony',   'Raj',    112.98,  70.43, False),
    (3, 'Kyle',     'Daniel',  91.96,  77.25, False),
    (3, 'duncan',   'PatrickF',98.40,  57.06, False),
    # ── Week 4 ──
    (4, 'Raj',      'Larson',  81.53,  70.39, False),
    (4, 'RyanC',    'David',  109.56,  51.18, False),
    (4, 'Kyle',     'PatrickF',68.86,  52.61, False),
    (4, 'duncan',   'Bradley', 90.17,  69.35, False),
    (4, 'Antony',   'Daniel', 131.70,  69.81, False),
    # ── Week 5 ──
    (5, 'Daniel',   'Larson',  90.14,  58.47, False),
    (5, 'David',    'Raj',     98.41,  67.63, False),
    (5, 'Bradley',  'RyanC',   95.34,  84.20, False),
    (5, 'duncan',   'Kyle',   112.46,  54.39, False),
    (5, 'Antony',   'PatrickF',83.10,  71.62, False),
    # ── Week 6 ──
    (6, 'Larson',   'PatrickF',59.94,  49.31, False),
    (6, 'Daniel',   'David',  129.27,  53.25, False),
    (6, 'Bradley',  'Raj',    118.09,  93.66, False),
    (6, 'RyanC',    'duncan', 122.55,  68.03, False),
    (6, 'Antony',   'Kyle',   115.46, 113.54, False),
    # ── Week 7 ──
    (7, 'Larson',   'Kyle',    70.70,  70.03, False),
    (7, 'PatrickF', 'David',   99.04,  66.78, False),
    (7, 'Bradley',  'Daniel', 113.25, 100.52, False),
    (7, 'Raj',      'RyanC',  101.87, 101.18, False),
    (7, 'Antony',   'duncan', 112.61, 108.70, False),
    # ── Week 8 ──
    (8, 'Antony',   'Larson',  99.13,  51.06, False),
    (8, 'Kyle',     'David',   73.25,  67.78, False),
    (8, 'PatrickF', 'Bradley', 93.69,  88.71, False),
    (8, 'Daniel',   'RyanC',   86.65,  81.83, False),
    (8, 'Raj',      'duncan',  95.25,  81.46, False),
    # ── Week 9 ──
    (9, 'duncan',   'Larson', 113.11,  52.79, False),
    (9, 'David',    'Antony', 109.07,  72.03, False),
    (9, 'Kyle',     'Bradley',115.59,  53.35, False),
    (9, 'RyanC',    'PatrickF',85.20,  81.06, False),
    (9, 'Daniel',   'Raj',    106.39,  73.78, False),
    # ── Week 10 ──
    (10, 'David',   'Larson', 149.16,  71.83, False),
    (10, 'Antony',  'Bradley', 90.19,  84.76, False),
    (10, 'Kyle',    'RyanC',   99.54,  62.46, False),
    (10, 'Raj',     'PatrickF',91.97,  47.59, False),
    (10, 'Daniel',  'duncan', 107.65,  71.36, False),
    # ── Week 11 ──
    (11, 'duncan',  'David',  112.23,  75.90, False),
    (11, 'Raj',     'Kyle',    90.78,  64.94, False),
    (11, 'RyanC',   'Antony',  87.01,  79.48, False),
    (11, 'Larson',  'Bradley',122.58, 104.28, False),
    (11, 'Daniel',  'PatrickF',102.37, 64.71, False),
    # ── Week 12 ──
    (12, 'Larson',  'RyanC',  110.11,  86.49, False),
    (12, 'Bradley', 'David',  135.06,  52.12, False),
    (12, 'Antony',  'Raj',     73.47,  66.79, False),
    (12, 'Kyle',    'Daniel', 119.96,  85.31, False),
    (12, 'duncan',  'PatrickF',101.80, 84.06, False),
    # ── Week 13 ──
    (13, 'Larson',  'Raj',     96.22,  80.35, False),
    (13, 'David',   'RyanC',   74.65,  68.15, False),
    (13, 'PatrickF','Kyle',    99.84,  88.44, False),
    (13, 'duncan',  'Bradley',109.18,  91.23, False),
    (13, 'Antony',  'Daniel',  89.20,  69.98, False),
    # ── Playoffs ──
    # Wk 14 round 1 (seeds 3v5, 4v6; seeds 1 & 2 had byes)
    (14, 'RyanC',   'Daniel', 124.68, 111.20,  True),
    (14, 'Kyle',    'Larson', 101.71,  70.42,  True),
    # Wk 15 semis + consolation
    (15, 'duncan',  'RyanC',   96.66,  80.48,  True),
    (15, 'Antony',  'Kyle',   103.78,  89.25,  True),
    (15, 'Daniel',  'Larson',  94.30,  67.60,  True),
    # Wk 16 championship + 3rd place
    (16, 'duncan',  'Antony', 132.95,  69.45,  True),
    (16, 'RyanC',   'Kyle',    94.03,  82.18,  True),
]

# ---------------------------------------------------------------------------
# Parse existing h2hData
# ---------------------------------------------------------------------------
html_txt = HTML.read_text(encoding='utf-8')
start = html_txt.index('var h2hData = {')
end   = html_txt.index('\n};', start) + 3
h2h_block = html_txt[start:end]

outer_re = re.compile(r"^\s*'(\w+)':\s*\{$", re.MULTILINE)
entry_re = re.compile(
    r"'(\w+)':\s*\{w1:(-?\d+),w2:(-?\d+),pf1:([\d.]+),pf2:([\d.]+),"
    r"big1:([\d.]+|null),big2:([\d.]+|null),"
    r"last:\{winner:'(\w+)',score1:([\d.]+),score2:([\d.]+),season:'(\w+)'\},"
    r"playoffs:(\d+),seasons:(\d+)\}"
)

h2h = {}
cur_outer = None
for line in h2h_block.split('\n'):
    om = outer_re.match(line)
    if om:
        cur_outer = om.group(1)
        h2h[cur_outer] = {}
        continue
    em = entry_re.search(line)
    if em and cur_outer:
        inner = em.group(1)
        h2h[cur_outer][inner] = {
            'w1': int(em.group(2)), 'w2': int(em.group(3)),
            'pf1': float(em.group(4)), 'pf2': float(em.group(5)),
            'big1': None if em.group(6) == 'null' else float(em.group(6)),
            'big2': None if em.group(7) == 'null' else float(em.group(7)),
            'last': {'winner': em.group(8), 'score1': float(em.group(9)),
                     'score2': float(em.group(10)), 'season': em.group(11)},
            'playoffs': int(em.group(12)),
            'seasons': int(em.group(13))
        }

def get_or_create(mgr_a, mgr_b):
    if mgr_a in h2h and mgr_b in h2h[mgr_a]:
        return mgr_a, mgr_b
    if mgr_b in h2h and mgr_a in h2h[mgr_b]:
        return mgr_b, mgr_a
    # New pair
    outer, inner = (mgr_a, mgr_b) if mgr_a < mgr_b else (mgr_b, mgr_a)
    if outer not in h2h:
        h2h[outer] = {}
    h2h[outer][inner] = {
        'w1': 0, 'w2': 0, 'pf1': 0.0, 'pf2': 0.0,
        'big1': None, 'big2': None,
        'last': None, 'playoffs': 0, 'seasons': 0
    }
    print(f"  NEW PAIR created: {outer} → {inner}")
    return outer, inner

# ---------------------------------------------------------------------------
# Process games
# ---------------------------------------------------------------------------
seen = set()
season_pairs = set()

for (wk, mgr_a, mgr_b, score_a, score_b, is_playoff) in GAMES_2009:
    key = tuple(sorted([mgr_a, mgr_b])) + (wk,)
    if key in seen:
        print(f"DUPLICATE: {mgr_a} vs {mgr_b} wk {wk}")
        continue
    seen.add(key)

    outer, inner = get_or_create(mgr_a, mgr_b)
    d = h2h[outer][inner]

    s_outer = score_a if outer == mgr_a else score_b
    s_inner = score_b if outer == mgr_a else score_a

    if s_outer > s_inner:
        d['w1'] += 1
    else:
        d['w2'] += 1

    d['pf1'] = round(d['pf1'] + s_outer, 2)
    d['pf2'] = round(d['pf2'] + s_inner, 2)

    if d['big1'] is None or s_outer > d['big1']:
        d['big1'] = s_outer
    if d['big2'] is None or s_inner > d['big2']:
        d['big2'] = s_inner

    if is_playoff:
        d['playoffs'] += 1

    season_pairs.add((outer, inner))

# Increment seasons (2009 is older than existing data; do NOT touch 'last')
for (outer, inner) in season_pairs:
    h2h[outer][inner]['seasons'] += 1

# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------
total_games = sum(h2h[o][i]['w1'] + h2h[o][i]['w2'] for o in h2h for i in h2h[o])
total_pairs = sum(len(v) for v in h2h.values())
print(f"\n2009 games processed : {len(seen)}")
print(f"Total pairs          : {total_pairs}")
print(f"Total games          : {total_games}")

# ---------------------------------------------------------------------------
# Serialize
# ---------------------------------------------------------------------------
def fv(v):
    if v is None: return 'null'
    if isinstance(v, float): return f"{v:.2f}"
    return str(v)

lines = ['var h2hData = {']
for outer in sorted(h2h.keys()):
    lines.append(f"  '{outer}': {{")
    entries = []
    for inner in sorted(h2h[outer].keys()):
        d = h2h[outer][inner]
        L = d['last']
        if L:
            ls = (f"last:{{winner:'{L['winner']}',score1:{L['score1']:.2f},"
                  f"score2:{L['score2']:.2f},season:'{L['season']}'}}")
        else:
            ls = "last:null"
        entries.append(
            f"    '{inner}': {{w1:{d['w1']},w2:{d['w2']},"
            f"pf1:{d['pf1']:.2f},pf2:{d['pf2']:.2f},"
            f"big1:{fv(d['big1'])},big2:{fv(d['big2'])},"
            f"{ls},"
            f"playoffs:{d['playoffs']},seasons:{d['seasons']}}}"
        )
    lines.append(',\n'.join(entries))
    lines.append('  },')
lines.append('};')
new_block = '\n'.join(lines)

new_html = html_txt[:start] + new_block + html_txt[end:]

# Update footnote
new_html = new_html.replace(
    "H2H data complete · 2011–2025 seasons (15 seasons) · 2009 had different membership",
    "H2H data complete · 2009–2025 seasons (16 seasons)"
)

HTML.write_text(new_html, encoding='utf-8')
print("Done — kdp_report.html updated.")
