import re
from collections import defaultdict

# ── 2022 SCHEDULE DATA ──────────────────────────────────────────────────────
SCHED_2022 = {
    'Antony': [
        (1,'duncan',154.17,114.97),(2,'RyanC',126.68,99.45),(3,'PatrickF',101.50,105.00),
        (4,'David',138.58,112.06),(5,'Jeremy',156.45,77.70),(6,'Ryan',92.72,93.42),
        (7,'Kyle',94.19,89.58),(8,'Raj',100.26,137.31),(9,'Daniel',125.56,109.79),
        (10,'duncan',101.83,134.06),(11,'RyanC',130.04,105.18),(12,'PatrickF',107.21,132.11),
        (13,'David',126.26,149.53),(14,'Jeremy',106.74,100.29),(15,'Ryan',132.12,106.23),
    ],
    'Daniel': [
        (1,'Raj',124.82,105.59),(2,'duncan',141.25,146.21),(3,'RyanC',118.30,72.72),
        (4,'PatrickF',108.62,74.50),(5,'David',112.28,119.18),(6,'Jeremy',108.51,111.37),
        (7,'Ryan',94.87,112.78),(8,'Kyle',156.06,125.91),(9,'Antony',109.79,125.56),
        (10,'Raj',102.00,96.61),(11,'duncan',101.33,91.74),(12,'RyanC',141.55,106.64),
        (13,'PatrickF',159.37,107.66),(14,'David',97.35,127.64),(15,'Jeremy',144.50,118.10),
    ],
    'David': [
        (1,'Jeremy',130.03,126.08),(2,'Ryan',135.05,146.60),(3,'Kyle',118.92,116.30),
        (4,'Antony',112.06,138.58),(5,'Daniel',119.18,112.28),(6,'duncan',101.32,104.74),
        (7,'RyanC',108.93,131.87),(8,'PatrickF',134.24,96.46),(9,'Raj',73.44,127.84),
        (10,'Jeremy',111.86,102.15),(11,'Ryan',135.42,146.43),(12,'Kyle',132.16,134.87),
        (13,'Antony',149.53,126.26),(14,'Daniel',127.64,97.35),(15,'duncan',105.33,116.17),
    ],
    'Jeremy': [
        (1,'David',126.08,130.03),(2,'Raj',147.72,81.00),(3,'Ryan',98.39,101.58),
        (4,'Kyle',101.50,128.15),(5,'Antony',77.70,156.45),(6,'Daniel',111.37,108.51),
        (7,'duncan',82.16,123.78),(8,'RyanC',129.35,133.16),(9,'PatrickF',122.36,83.70),
        (10,'David',102.15,111.86),(11,'Raj',71.07,72.03),(12,'Ryan',103.40,98.97),
        (13,'Kyle',86.83,88.45),(14,'Antony',100.29,106.74),(15,'Daniel',118.10,144.50),
    ],
    'Kyle': [
        (1,'RyanC',89.51,72.55),(2,'PatrickF',92.08,149.29),(3,'David',116.30,118.92),
        (4,'Jeremy',128.15,101.50),(5,'Ryan',173.28,131.34),(6,'Raj',124.46,84.12),
        (7,'Antony',89.58,94.19),(8,'Daniel',125.91,156.06),(9,'duncan',144.39,161.02),
        (10,'RyanC',123.11,102.72),(11,'PatrickF',135.32,132.19),(12,'David',134.87,132.16),
        (13,'Jeremy',88.45,86.83),(14,'Ryan',110.76,124.66),(15,'Raj',150.74,129.01),
    ],
    'PatrickF': [
        (1,'Ryan',99.36,142.90),(2,'Kyle',149.29,92.08),(3,'Antony',105.00,101.50),
        (4,'Daniel',74.50,108.62),(5,'duncan',131.18,117.36),(6,'RyanC',105.15,76.00),
        (7,'Raj',154.04,76.89),(8,'David',96.46,134.24),(9,'Jeremy',83.70,122.36),
        (10,'Ryan',112.50,110.10),(11,'Kyle',132.19,135.32),(12,'Antony',132.11,107.21),
        (13,'Daniel',107.66,159.37),(14,'duncan',142.06,80.63),(15,'RyanC',101.72,84.44),
    ],
    'Raj': [
        (1,'Daniel',105.59,124.82),(2,'Jeremy',81.00,147.72),(3,'duncan',99.00,102.17),
        (4,'Ryan',91.77,128.80),(5,'RyanC',132.13,123.36),(6,'Kyle',84.12,124.46),
        (7,'PatrickF',76.89,154.04),(8,'Antony',137.31,100.26),(9,'David',127.84,73.44),
        (10,'Daniel',96.61,102.00),(11,'Jeremy',72.03,71.07),(12,'duncan',138.93,126.80),
        (13,'Ryan',75.08,110.62),(14,'RyanC',84.69,169.76),(15,'Kyle',129.01,150.74),
    ],
    'Ryan': [
        (1,'PatrickF',142.90,99.36),(2,'David',146.60,135.05),(3,'Jeremy',101.58,98.39),
        (4,'Raj',128.80,91.77),(5,'Kyle',131.34,173.28),(6,'Antony',93.42,92.72),
        (7,'Daniel',112.78,94.87),(8,'duncan',112.37,111.71),(9,'RyanC',123.71,102.84),
        (10,'PatrickF',110.10,112.50),(11,'David',146.43,135.42),(12,'Jeremy',98.97,103.40),
        (13,'Raj',110.62,75.08),(14,'Kyle',124.66,110.76),(15,'Antony',106.23,132.12),
    ],
    'RyanC': [
        (1,'Kyle',72.55,89.51),(2,'Antony',99.45,126.68),(3,'Daniel',72.72,118.30),
        (4,'duncan',159.88,68.50),(5,'Raj',123.36,132.13),(6,'PatrickF',76.00,105.15),
        (7,'David',131.87,108.93),(8,'Jeremy',133.16,129.35),(9,'Ryan',102.84,123.71),
        (10,'Kyle',102.72,123.11),(11,'Antony',105.18,130.04),(12,'Daniel',106.64,141.55),
        (13,'duncan',117.35,128.30),(14,'Raj',84.69,169.76),(15,'PatrickF',84.44,101.72),
    ],
    'duncan': [
        (1,'Antony',114.97,154.17),(2,'Daniel',146.21,141.25),(3,'Raj',102.17,99.00),
        (4,'RyanC',68.50,159.88),(5,'PatrickF',117.36,131.18),(6,'David',104.74,101.32),
        (7,'Jeremy',123.78,82.16),(8,'Ryan',111.71,112.37),(9,'Kyle',161.02,144.39),
        (10,'Antony',134.06,101.83),(11,'Daniel',91.74,101.33),(12,'Raj',126.80,138.93),
        (13,'RyanC',128.30,117.35),(14,'PatrickF',80.63,142.06),(15,'David',116.17,105.33),
    ],
}

# Championship bracket SFs (wk16), Final + 3rd (wk17)
# Consolation: 5th/6th and 7th/8th (wk17 only - no wk16 consolation games found)
PLAYOFFS_2022 = [
    (16, 'Ryan',     'Antony',   82.83, 128.54, True),
    (16, 'Kyle',     'Daniel',  124.99,  77.64, True),
    (17, 'Antony',   'Kyle',    108.96,  90.91, True),
    (17, 'Ryan',     'Daniel',   74.09,  86.98, True),
    (17, 'duncan',   'Raj',      94.81,  67.21, True),
    (17, 'PatrickF', 'David',    77.71,  82.92, True),
]

# ── PARSE EXISTING h2hData FROM kdp_report.html (line-by-line) ──────────────
with open('kdp_report.html') as f:
    html = f.read()

h2h_start = html.find('var h2hData = {')
h2h_end   = html.find('\n};', h2h_start) + 3
js_block  = html[h2h_start:h2h_end]

entry_re = re.compile(
    r"'(\w+)':\s*\{w1:(-?\d+),w2:(-?\d+),pf1:([\d.]+),pf2:([\d.]+),"
    r"big1:([\d.]+|null),big2:([\d.]+|null),"
    r"last:\{winner:'(\w+)',score1:([\d.]+),score2:([\d.]+),season:'(\w+)'\},"
    r"playoffs:(\d+),seasons:(\d+)\}"
)
outer_re = re.compile(r"^\s*'(\w+)':\s*\{$")

existing = {}
cur_outer = None
for line in js_block.split('\n'):
    om = outer_re.match(line)
    if om:
        cur_outer = om.group(1)
        existing[cur_outer] = {}
        continue
    if cur_outer:
        m = entry_re.search(line)
        if m:
            existing[cur_outer][m.group(1)] = {
                'w1': int(m.group(2)), 'w2': int(m.group(3)),
                'pf1': float(m.group(4)), 'pf2': float(m.group(5)),
                'big1': None if m.group(6)=='null' else float(m.group(6)),
                'big2': None if m.group(7)=='null' else float(m.group(7)),
                'last': {'winner': m.group(8), 'score1': float(m.group(9)),
                         'score2': float(m.group(10)), 'season': m.group(11)},
                'playoffs': int(m.group(12)), 'seasons': int(m.group(13))
            }

total_pairs = sum(len(v) for v in existing.values())
total_games = sum(e['w1']+e['w2'] for d in existing.values() for e in d.values())
print(f"Parsed {total_pairs} pairs, {total_games} game records from kdp_report.html")

# ── HELPER ───────────────────────────────────────────────────────────────────
def get_or_create(a, b):
    outer, inner = (a, b) if a < b else (b, a)
    if outer not in existing:
        existing[outer] = {}
    if inner not in existing[outer]:
        existing[outer][inner] = {
            'w1': 0, 'w2': 0, 'pf1': 0.0, 'pf2': 0.0,
            'big1': None, 'big2': None, 'last': None,
            'playoffs': 0, 'seasons': 0
        }
    return outer, inner, existing[outer][inner]

# ── COLLECT 2022 GAMES ───────────────────────────────────────────────────────
games = defaultdict(list)
seen  = set()

for mgr, schedule in SCHED_2022.items():
    for (wk, opp, my_s, opp_s) in schedule:
        dedup_key = tuple(sorted([mgr, opp])) + (wk,)
        if dedup_key in seen:
            continue
        seen.add(dedup_key)
        outer, inner = (mgr, opp) if mgr < opp else (opp, mgr)
        if mgr < opp:
            games[(outer, inner)].append((my_s, opp_s, False))
        else:
            games[(outer, inner)].append((opp_s, my_s, False))

for (wk, m1, m2, s1, s2, is_po) in PLAYOFFS_2022:
    outer, inner = (m1, m2) if m1 < m2 else (m2, m1)
    if m1 < m2:
        games[(outer, inner)].append((s1, s2, is_po))
    else:
        games[(outer, inner)].append((s2, s1, is_po))

total_new = sum(len(v) for v in games.values())
print(f"2022 games collected: {total_new} (expect 81: 75 reg + 6 playoff)")

# ── MERGE ────────────────────────────────────────────────────────────────────
seasons_added = set()
for (outer, inner), game_list in games.items():
    _, _, entry = get_or_create(outer, inner)

    if (outer, inner) not in seasons_added:
        entry['seasons'] += 1
        seasons_added.add((outer, inner))

    for (s_outer, s_inner, is_po) in game_list:
        if s_outer > s_inner:
            entry['w1'] += 1
        else:
            entry['w2'] += 1
        entry['pf1'] = round(entry['pf1'] + s_outer, 2)
        entry['pf2'] = round(entry['pf2'] + s_inner, 2)
        if entry['big1'] is None or s_outer > entry['big1']:
            entry['big1'] = s_outer
        if entry['big2'] is None or s_inner > entry['big2']:
            entry['big2'] = s_inner
        if is_po:
            entry['playoffs'] += 1
        # 2022 is OLDER — only set 'last' if no prior data
        if entry['last'] is None:
            winner = outer if s_outer > s_inner else inner
            entry['last'] = {'winner': winner, 'score1': s_outer,
                             'score2': s_inner, 'season': '22'}

# ── WRITE h2h_all.js ─────────────────────────────────────────────────────────
lines = ['var h2hData = {']
outer_keys = sorted(existing.keys())
for i, outer in enumerate(outer_keys):
    lines.append(f"  '{outer}': {{")
    inner_items = list(existing[outer].items())
    for j, (inner, e) in enumerate(inner_items):
        last = e['last']
        last_str = (f"{{winner:'{last['winner']}',score1:{last['score1']:.2f},"
                    f"score2:{last['score2']:.2f},season:'{last['season']}'}}"
                    if last else 'null')
        b1 = f"{e['big1']:.2f}" if e['big1'] is not None else 'null'
        b2 = f"{e['big2']:.2f}" if e['big2'] is not None else 'null'
        comma = '' if j == len(inner_items)-1 else ','
        lines.append(
            f"    '{inner}': {{w1:{e['w1']},w2:{e['w2']},"
            f"pf1:{e['pf1']:.2f},pf2:{e['pf2']:.2f},"
            f"big1:{b1},big2:{b2},"
            f"last:{last_str},"
            f"playoffs:{e['playoffs']},seasons:{e['seasons']}}}{comma}"
        )
    comma = '' if i == len(outer_keys)-1 else ','
    lines.append(f"  }}{comma}")
lines.append('};')

out = '\n'.join(lines)
with open('h2h_all.js', 'w') as f:
    f.write(out)

total_pairs_new = sum(len(v) for v in existing.values())
total_games_new = sum(e['w1']+e['w2'] for d in existing.values() for e in d.values())
print(f"Wrote h2h_all.js: {total_pairs_new} pairs, {total_games_new} total games")

# Spot checks
checks = [
    ('Antony', 'Ryan'),     # should now have 2022 games added
    ('Antony', 'Kyle'),     # playoff game (championship final) in 2022
    ('Daniel', 'Jeremy'),   # should have 3 prior seasons + 1 new = 4
]
for a, b in checks:
    outer, inner = (a,b) if a<b else (b,a)
    e = existing.get(outer,{}).get(inner,{})
    print(f"  {outer} vs {inner}: w1={e.get('w1')},w2={e.get('w2')},seasons={e.get('seasons')},playoffs={e.get('playoffs')},last_season={e.get('last',{}).get('season')}")
