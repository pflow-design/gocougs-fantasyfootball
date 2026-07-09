"""
Generate H2H data for 2023 KDP season and merge with existing 2024+2025 data.
2023: league 211296
Champion: Jeremy (Clappin' Cheeks)
"""

import json, re

# Team -> Manager mapping for 2023
TEAM_MGR_2023 = {
    "Hugh Winn's":          'duncan',
    'Catching Kelce':       'Kyle',
    'ExtraVirginOilofOlave':'David',
    "Clappin' Cheeks":      'Jeremy',
    'Hit Somebody':         'Ryan',
    'From Texas with love': 'PatrickF',
    'My Ball Zach Ertz':    'Daniel',
    'Moore Bijan please':   'Antony',
    'shmoney maker':        'Raj',
    'No Moore Problems':    'RyanC',
}

# Schedule format: (wk, opponent_manager, result, my_score, opp_score)
SCHED_2023 = {
    'duncan': [
        (1,'Antony','W',115.34,83.79),(2,'Raj','L',110.70,124.59),
        (3,'Jeremy','L',109.64,136.24),(4,'Kyle','W',102.12,84.84),
        (5,'RyanC','W',165.87,97.46),(6,'David','L',91.81,94.64),
        (7,'Daniel','W',127.26,66.21),(8,'Ryan','L',107.23,127.25),
        (9,'PatrickF','W',96.90,86.03),(10,'Antony','W',145.99,112.55),
        (11,'Raj','W',108.91,107.03),(12,'Jeremy','L',126.23,136.66),
        (13,'Kyle','L',119.64,131.27),(14,'RyanC','L',116.24,136.34),
        (15,'David','W',113.40,100.28),
    ],
    'Kyle': [
        (1,'David','L',61.96,162.54),(2,'Daniel','W',125.08,103.91),
        (3,'Ryan','L',103.91,112.86),(4,'duncan','L',84.84,102.12),
        (5,'Antony','W',136.19,127.41),(6,'Raj','L',110.95,119.53),
        (7,'Jeremy','W',119.19,103.94),(8,'PatrickF','L',81.07,126.93),
        (9,'RyanC','W',122.44,116.63),(10,'David','L',77.38,110.37),
        (11,'Daniel','L',89.54,92.14),(12,'Ryan','W',126.56,114.01),
        (13,'duncan','W',131.27,119.64),(14,'Antony','L',86.37,153.67),
        (15,'Raj','W',118.60,97.00),
    ],
    'David': [
        (1,'Kyle','W',162.54,61.96),(2,'RyanC','L',118.54,132.29),
        (3,'PatrickF','W',145.12,133.20),(4,'Daniel','L',58.42,112.15),
        (5,'Ryan','L',127.57,150.82),(6,'duncan','W',94.64,91.81),
        (7,'Antony','L',109.07,114.91),(8,'Raj','L',101.85,137.24),
        (9,'Jeremy','L',125.36,149.23),(10,'Kyle','W',110.37,77.38),
        (11,'RyanC','L',122.03,134.60),(12,'PatrickF','W',133.91,96.80),
        (13,'Daniel','W',145.05,117.10),(14,'Ryan','L',103.74,129.59),
        (15,'duncan','L',100.28,113.40),
    ],
    'Jeremy': [
        (1,'Daniel','W',116.86,82.71),(2,'Ryan','W',104.20,76.87),
        (3,'duncan','W',136.24,109.64),(4,'Antony','L',129.56,146.83),
        (5,'Raj','L',98.82,110.00),(6,'PatrickF','W',119.97,118.75),
        (7,'Kyle','L',103.94,119.19),(8,'RyanC','L',130.41,144.87),
        (9,'David','W',149.23,125.36),(10,'Daniel','W',168.52,108.94),
        (11,'Ryan','L',100.41,105.43),(12,'duncan','W',136.66,126.23),
        (13,'Antony','W',138.18,114.61),(14,'Raj','L',98.21,113.14),
        (15,'PatrickF','W',100.34,84.89),
    ],
    'Ryan': [
        (1,'Raj','W',139.44,87.07),(2,'Jeremy','L',76.87,104.20),
        (3,'Kyle','W',112.86,103.91),(4,'RyanC','L',121.16,139.08),
        (5,'David','W',150.82,127.57),(6,'Daniel','W',114.29,89.27),
        (7,'PatrickF','W',136.14,94.32),(8,'duncan','W',127.25,107.23),
        (9,'Antony','W',82.04,75.44),(10,'Raj','W',140.81,61.77),
        (11,'Jeremy','W',105.43,100.41),(12,'Kyle','L',114.01,126.56),
        (13,'RyanC','L',126.30,157.86),(14,'David','W',129.59,103.74),
        (15,'Daniel','W',102.41,98.31),
    ],
    'PatrickF': [
        (1,'RyanC','W',114.19,95.17),(2,'Antony','W',136.43,110.05),
        (3,'David','L',133.20,145.12),(4,'Raj','L',103.82,126.91),
        (5,'Daniel','W',107.68,99.01),(6,'Jeremy','L',118.75,119.97),
        (7,'Ryan','L',94.32,136.14),(8,'Kyle','W',126.93,81.07),
        (9,'duncan','L',86.03,96.90),(10,'RyanC','L',130.21,130.25),
        (11,'Antony','L',132.77,139.80),(12,'David','L',96.80,133.91),
        (13,'Raj','L',85.16,126.28),(14,'Daniel','L',87.08,112.27),
        (15,'Jeremy','L',84.89,100.34),
    ],
    'Daniel': [
        (1,'Jeremy','L',82.71,116.86),(2,'Kyle','L',103.91,125.08),
        (3,'RyanC','L',115.90,145.78),(4,'David','W',112.15,58.42),
        (5,'PatrickF','L',99.01,107.68),(6,'Ryan','L',89.27,114.29),
        (7,'duncan','L',66.21,127.26),(8,'Antony','W',139.92,89.62),
        (9,'Raj','L',119.15,120.62),(10,'Jeremy','L',108.94,168.52),
        (11,'Kyle','W',92.14,89.54),(12,'RyanC','L',126.06,158.38),
        (13,'David','L',117.10,145.05),(14,'PatrickF','W',112.27,87.08),
        (15,'Ryan','L',98.31,102.41),
    ],
    'Antony': [
        (1,'duncan','L',83.79,115.34),(2,'PatrickF','L',110.05,136.43),
        (3,'Raj','W',116.64,108.25),(4,'Jeremy','W',146.83,129.56),
        (5,'Kyle','L',127.41,136.19),(6,'RyanC','W',108.46,104.73),
        (7,'David','W',114.91,109.07),(8,'Daniel','L',89.62,139.92),
        (9,'Ryan','L',75.44,82.04),(10,'duncan','L',112.55,145.99),
        (11,'PatrickF','W',139.80,132.77),(12,'Raj','W',160.47,149.63),
        (13,'Jeremy','L',114.61,138.18),(14,'Kyle','W',153.67,86.37),
        (15,'RyanC','L',127.98,160.72),
    ],
    'Raj': [
        (1,'Ryan','L',87.07,139.44),(2,'duncan','W',124.59,110.70),
        (3,'Antony','L',108.25,116.64),(4,'PatrickF','W',126.91,103.82),
        (5,'Jeremy','W',110.00,98.82),(6,'Kyle','W',119.53,110.95),
        (7,'RyanC','L',123.47,124.47),(8,'David','W',137.24,101.85),
        (9,'Daniel','W',120.62,119.15),(10,'Ryan','L',61.77,140.81),
        (11,'duncan','L',107.03,108.91),(12,'Antony','L',149.63,160.47),
        (13,'PatrickF','W',126.28,85.16),(14,'Jeremy','W',113.14,98.21),
        (15,'Kyle','L',97.00,118.60),
    ],
    'RyanC': [
        (1,'PatrickF','L',95.17,114.19),(2,'David','W',132.29,118.54),
        (3,'Daniel','W',145.78,115.90),(4,'Ryan','W',139.08,121.16),
        (5,'duncan','L',97.46,165.87),(6,'Antony','L',104.73,108.46),
        (7,'Raj','W',124.47,123.47),(8,'Jeremy','W',144.87,130.41),
        (9,'Kyle','L',116.63,122.44),(10,'PatrickF','W',130.25,130.21),
        (11,'David','W',134.60,122.03),(12,'Daniel','W',158.38,126.06),
        (13,'Ryan','W',157.86,126.30),(14,'duncan','W',136.34,116.24),
        (15,'Antony','W',160.72,127.98),
    ],
}

# Playoffs 2023 (format: team1, team2, score1, score2)
# All 4 championship bracket games
PLAYOFFS_2023 = [
    ('RyanC', 'duncan',  160.41, 105.19),  # SF1 wk16, RyanC wins
    ('Ryan',  'Jeremy',   99.57, 128.75),  # SF2 wk16, Jeremy wins
    ('RyanC', 'Jeremy',   95.91, 144.82),  # Final wk17, Jeremy wins
    ('Ryan',  'duncan',  141.93,  91.26),  # 3rd Place wk17, Ryan wins
]

MGRS_2023 = ['Raj','PatrickF','RyanC','David','Kyle','Antony','daniel' if False else 'Daniel','Ryan','Jeremy','duncan']
MGRS = sorted(['Raj','PatrickF','RyanC','David','Kyle','Antony','Daniel','Ryan','Jeremy','duncan'])
print("Sorted managers:", MGRS)

# ──────────────────────────────────────────────
# Build 2023 h2h from schedules (deduplication via canonical pair key)
# ──────────────────────────────────────────────
season = '23'
games = {}  # (a,b) -> list of (score_a, score_b, is_playoff)

def add_game(m1, m2, s1, s2, is_po=False):
    key = (m1,m2) if m1 < m2 else (m2,m1)
    if key not in games:
        games[key] = []
    if m1 < m2:
        games[key].append((s1, s2, is_po))
    else:
        games[key].append((s2, s1, is_po))

# Add regular season games (deduplicate: only process each unique game once)
seen = set()
for mgr, schedule in SCHED_2023.items():
    for wk, opp, result, my_score, opp_score in schedule:
        key = tuple(sorted([mgr, opp])) + (wk,)
        if key in seen:
            continue
        seen.add(key)
        add_game(mgr, opp, my_score, opp_score)

print(f"Regular season games: {len(seen)}")

# Add playoff games
for m1, m2, s1, s2 in PLAYOFFS_2023:
    add_game(m1, m2, s1, s2, is_po=True)

total = sum(len(v) for v in games.values())
print(f"Total 2023 games: {total} (expected: 75 reg + 4 po = 79)")

# ──────────────────────────────────────────────
# Read existing h2h_2024_2025.js and parse
# ──────────────────────────────────────────────
with open('/sessions/elegant-eloquent-hamilton/mnt/outputs/h2h_2024_2025.js') as f:
    existing_js = f.read()

# Parse JS into Python dict using regex
def parse_h2h_js(js_text):
    """Parse the h2hData JS object into nested Python dicts."""
    h2h = {}
    # Extract the content between var h2hData = { and };
    m = re.search(r'var h2hData = \{(.*)\};', js_text, re.DOTALL)
    if not m:
        raise ValueError("Could not find h2hData")
    content = m.group(1)

    # Parse top-level keys
    top_pattern = re.compile(r"'(\w+)':\s*\{([^{}]+(?:\{[^{}]*\}[^{}]*)*)\}", re.DOTALL)
    for top_match in top_pattern.finditer(content):
        mgr_a = top_match.group(1)
        inner = top_match.group(2)
        h2h[mgr_a] = {}

        # Parse inner key-value pairs
        inner_pattern = re.compile(
            r"'(\w+)':\s*\{w1:(-?\d+),w2:(-?\d+),pf1:([\d.]+),pf2:([\d.]+),"
            r"big1:([\d.]+|null),big2:([\d.]+|null),"
            r"last:\{winner:'(\w+)',score1:([\d.]+),score2:([\d.]+),season:'(\w+)'\},"
            r"playoffs:(\d+),seasons:(\d+)\}"
        )
        for im in inner_pattern.finditer(inner):
            mgr_b = im.group(1)
            def n(v): return None if v == 'null' else float(v)
            h2h[mgr_a][mgr_b] = {
                'w1': int(im.group(2)), 'w2': int(im.group(3)),
                'pf1': float(im.group(4)), 'pf2': float(im.group(5)),
                'big1': n(im.group(6)), 'big2': n(im.group(7)),
                'last': {'winner': im.group(8), 'score1': float(im.group(9)),
                         'score2': float(im.group(10)), 'season': im.group(11)},
                'playoffs': int(im.group(11) if False else im.group(11)),
                'seasons': int(im.group(12) if False else im.group(12)),
            }
            # Fix: playoffs is group(11)? No:
            # groups: 1=mgrB, 2=w1, 3=w2, 4=pf1, 5=pf2, 6=big1, 7=big2,
            #         8=winner, 9=score1, 10=score2, 11=season_str, 12=playoffs, 13=seasons
    return h2h

# Re-parse with corrected group indices
def parse_h2h_js_v2(js_text):
    h2h = {}
    m = re.search(r'var h2hData = \{(.*)\};', js_text, re.DOTALL)
    content = m.group(1)

    top_pattern = re.compile(r"'(\w+)':\s*\{([^{}]+(?:\{[^{}]*\}[^{}]*)*)\}", re.DOTALL)
    for top_match in top_pattern.finditer(content):
        mgr_a = top_match.group(1)
        inner = top_match.group(2)
        h2h[mgr_a] = {}

        inner_pattern = re.compile(
            r"'(\w+)':\s*\{"
            r"w1:(-?\d+),w2:(-?\d+),"
            r"pf1:([\d.]+),pf2:([\d.]+),"
            r"big1:([\d.]+|null),big2:([\d.]+|null),"
            r"last:\{winner:'(\w+)',score1:([\d.]+),score2:([\d.]+),season:'(\w+)'\},"
            r"playoffs:(\d+),seasons:(\d+)\}"
        )
        for im in inner_pattern.finditer(inner):
            def n(v): return None if v == 'null' else float(v)
            mgr_b = im.group(1)
            h2h[mgr_a][mgr_b] = {
                'w1': int(im.group(2)), 'w2': int(im.group(3)),
                'pf1': float(im.group(4)), 'pf2': float(im.group(5)),
                'big1': n(im.group(6)), 'big2': n(im.group(7)),
                'last': {
                    'winner': im.group(8),
                    'score1': float(im.group(9)),
                    'score2': float(im.group(10)),
                    'season': im.group(11),
                },
                'playoffs': int(im.group(12)),
                'seasons': int(im.group(13)),
            }
    return h2h

existing = parse_h2h_js_v2(existing_js)
print(f"Loaded existing h2h pairs: {sum(len(v) for v in existing.values())}")

# ──────────────────────────────────────────────
# Merge 2023 data into existing h2h
# ──────────────────────────────────────────────
def get_entry(h2h, a, b):
    """Get or create h2h entry for pair (a,b) with a<b."""
    if a not in h2h:
        h2h[a] = {}
    if b not in h2h[a]:
        h2h[a][b] = {'w1':0,'w2':0,'pf1':0.0,'pf2':0.0,
                     'big1':None,'big2':None,'last':None,
                     'playoffs':0,'seasons':0}
    return h2h[a][b]

for (a, b), game_list in games.items():
    # a < b (canonical ordering)
    e = get_entry(existing, a, b)
    e['seasons'] += 1  # Add 1 for this new season

    for s_a, s_b, is_po in game_list:
        if s_a > s_b:
            e['w1'] += 1
        else:
            e['w2'] += 1
        e['pf1'] = round(e['pf1'] + s_a, 2)
        e['pf2'] = round(e['pf2'] + s_b, 2)
        if e['big1'] is None or s_a > e['big1']:
            e['big1'] = s_a
        if e['big2'] is None or s_b > e['big2']:
            e['big2'] = s_b
        if is_po:
            e['playoffs'] += 1
        # Update last: 2023 is older than 24/25, so only update if no last set
        # Actually, last = most recent matchup. Since 2023 < 2024 < 2025,
        # and we're adding 2023 data AFTER 2024+2025 data exists,
        # the existing "last" from 24/25 is MORE recent. Don't overwrite.
        # But if this pair has no last set yet (shouldn't happen since all were in 24+25),
        # set it.
        if e['last'] is None:
            winner = a if s_a > s_b else b
            e['last'] = {'winner': winner, 'score1': s_a, 'score2': s_b, 'season': season}

# Re-check: for any pair that only exists in 2023 (not in 24/25),
# set the last game properly. But since all 10 managers were in 24+25,
# all pairs should already exist. However, let's verify.
missing = []
for a in MGRS:
    for b in MGRS:
        if a >= b:
            continue
        found = (a in existing and b in existing[a]) or (b in existing and a in existing[b])
        if not found:
            missing.append((a,b))
if missing:
    print(f"WARNING: Missing pairs after merge: {missing}")
else:
    print("All 45 pairs present after merge ✓")

# ──────────────────────────────────────────────
# Emit updated JS
# ──────────────────────────────────────────────
def fmt(v):
    if v is None:
        return 'null'
    if isinstance(v, float):
        return f"{v:.2f}"
    return str(v)

lines = ['var h2hData = {']
for a in MGRS:
    if a not in existing:
        continue
    inner = existing[a]
    if not inner:
        continue
    lines.append(f"  '{a}': {{")
    items = list(inner.items())
    for i, (b, e) in enumerate(items):
        last = e['last']
        last_str = f"{{winner:'{last['winner']}',score1:{last['score1']:.2f},score2:{last['score2']:.2f},season:'{last['season']}'}}"
        comma = ',' if i < len(items)-1 else ''
        lines.append(
            f"    '{b}': {{w1:{e['w1']},w2:{e['w2']},"
            f"pf1:{e['pf1']:.2f},pf2:{e['pf2']:.2f},"
            f"big1:{fmt(e['big1'])},big2:{fmt(e['big2'])},"
            f"last:{last_str},"
            f"playoffs:{e['playoffs']},seasons:{e['seasons']}}}{comma}"
        )
    lines.append('  },')
lines.append('};')

js_output = '\n'.join(lines)
with open('/sessions/elegant-eloquent-hamilton/mnt/outputs/h2h_all.js', 'w') as f:
    f.write(js_output)

print(f"Written h2h_all.js ({len(js_output)} chars)")

# Validation
total_games = 0
total_wins = 0
for a, inner in existing.items():
    for b, e in inner.items():
        total_games += e['w1'] + e['w2']
        total_wins += e['w1'] + e['w2']
print(f"Total recorded game-sides (should be 2×total_games): {total_games}")
# Each game is counted once in h2hData (one side), so total_games = total unique games
# 2025: 79, 2024: 83, 2023: 79 = 241 total games
print(f"Expected total if 2023+2024+2025: 79+83+79 = 241")
