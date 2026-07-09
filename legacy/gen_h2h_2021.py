import re
from collections import defaultdict

# 2021 team mapping:
# scmid=1:Candyman→duncan, 2:DontStopFeedingMeELLIOTT→David, 3:MyBallZachErtz→Daniel
# scmid=4:RussellSprouts→RyanC, 5:AnythingButLast→Kyle, 6:WhatFoodDoYouWant→PatrickF
# scmid=7:TheKdpFootballTeam→Kyle2, 8:shneyMaker→Raj, 9:UpHillBattlers→Ryan, 10:ClappinCheeks→Jeremy

SCHED_2021 = {
    'duncan': [
        (1,'David',157.19,118.98),(2,'Daniel',154.97,122.40),(3,'RyanC',105.52,135.34),
        (4,'Kyle',86.32,159.52),(5,'PatrickF',160.01,96.72),(6,'Kyle2',114.61,109.45),
        (7,'Raj',151.97,79.87),(8,'Ryan',122.86,122.43),(9,'Jeremy',95.57,94.38),
        (10,'David',100.74,93.31),(11,'Daniel',116.44,106.59),(12,'RyanC',108.63,85.79),
        (13,'Kyle',131.69,115.22),(14,'PatrickF',92.65,123.72),(15,'Kyle2',68.46,146.41),
    ],
    'David': [
        (1,'duncan',118.98,157.19),(2,'Jeremy',122.05,121.82),(3,'Daniel',158.89,110.95),
        (4,'RyanC',111.37,112.75),(5,'Kyle',116.16,149.88),(6,'PatrickF',148.18,124.37),
        (7,'Kyle2',143.06,98.79),(8,'Raj',121.16,97.00),(9,'Ryan',85.26,89.60),
        (10,'duncan',93.31,100.74),(11,'Jeremy',84.88,144.81),(12,'Daniel',112.78,108.46),
        (13,'RyanC',136.91,116.91),(14,'Kyle',158.97,127.42),(15,'PatrickF',107.42,54.91),
    ],
    'Daniel': [
        (1,'Ryan',102.03,118.49),(2,'duncan',122.40,154.97),(3,'David',110.95,158.89),
        (4,'Jeremy',122.57,124.23),(5,'RyanC',183.98,156.28),(6,'Kyle',133.89,141.37),
        (7,'PatrickF',134.91,116.18),(8,'Kyle2',100.85,96.25),(9,'Raj',126.41,62.10),
        (10,'Ryan',137.62,148.20),(11,'duncan',106.59,116.44),(12,'David',108.46,112.78),
        (13,'Jeremy',124.95,164.11),(14,'RyanC',131.99,142.91),(15,'Kyle',77.29,68.11),
    ],
    'RyanC': [
        (1,'Raj',109.37,137.24),(2,'Ryan',112.32,103.31),(3,'duncan',135.34,105.52),
        (4,'David',112.75,111.37),(5,'Daniel',156.28,183.98),(6,'Jeremy',129.56,98.26),
        (7,'Kyle',117.42,139.53),(8,'PatrickF',119.65,83.66),(9,'Kyle2',113.87,113.66),
        (10,'Raj',80.20,131.91),(11,'Ryan',125.38,174.86),(12,'duncan',85.79,108.63),
        (13,'David',116.91,136.91),(14,'Daniel',142.91,131.99),(15,'Jeremy',89.44,93.13),
    ],
    'Kyle': [
        (1,'Kyle2',125.19,117.12),(2,'Raj',126.68,109.38),(3,'Ryan',111.05,115.62),
        (4,'duncan',159.52,86.32),(5,'David',149.88,116.16),(6,'Daniel',141.37,133.89),
        (7,'RyanC',139.53,117.42),(8,'Jeremy',119.85,91.99),(9,'PatrickF',147.21,89.00),
        (10,'Kyle2',92.64,104.96),(11,'Raj',97.07,80.88),(12,'Ryan',131.67,124.60),
        (13,'duncan',115.22,131.69),(14,'David',127.42,158.97),(15,'Daniel',68.11,77.29),
    ],
    'PatrickF': [
        (1,'Jeremy',129.00,113.93),(2,'Kyle2',101.83,117.50),(3,'Raj',85.81,107.03),
        (4,'Ryan',111.79,164.95),(5,'duncan',96.72,160.01),(6,'David',124.37,148.18),
        (7,'Daniel',116.18,134.91),(8,'RyanC',83.66,119.65),(9,'Kyle',89.00,147.21),
        (10,'Jeremy',92.43,127.77),(11,'Kyle2',102.74,124.26),(12,'Raj',74.32,85.33),
        (13,'Ryan',104.35,114.38),(14,'duncan',123.72,92.65),(15,'David',54.91,107.42),
    ],
    'Kyle2': [
        (1,'Kyle',117.12,125.19),(2,'PatrickF',117.50,101.83),(3,'Jeremy',114.74,150.71),
        (4,'Raj',101.04,126.20),(5,'Ryan',119.83,151.77),(6,'duncan',109.45,114.61),
        (7,'David',98.79,143.06),(8,'Daniel',96.25,100.85),(9,'RyanC',113.66,113.87),
        (10,'Kyle',104.96,92.64),(11,'PatrickF',124.26,102.74),(12,'Jeremy',110.75,131.61),
        (13,'Raj',120.13,83.02),(14,'Ryan',106.71,95.03),(15,'duncan',146.41,68.46),
    ],
    'Raj': [
        (1,'RyanC',137.24,109.37),(2,'Kyle',109.38,126.68),(3,'PatrickF',107.03,85.81),
        (4,'Kyle2',126.20,101.04),(5,'Jeremy',172.15,126.71),(6,'Ryan',145.29,153.37),
        (7,'duncan',79.87,151.97),(8,'David',97.00,121.16),(9,'Daniel',62.10,126.41),
        (10,'RyanC',131.91,80.20),(11,'Kyle',80.88,97.07),(12,'PatrickF',85.33,74.32),
        (13,'Kyle2',83.02,120.13),(14,'Jeremy',139.72,138.87),(15,'Ryan',139.37,157.07),
    ],
    'Ryan': [
        (1,'Daniel',118.49,102.03),(2,'RyanC',103.31,112.32),(3,'Kyle',115.62,111.05),
        (4,'PatrickF',164.95,111.79),(5,'Kyle2',151.77,119.83),(6,'Raj',153.37,145.29),
        (7,'Jeremy',155.52,109.77),(8,'duncan',122.43,122.86),(9,'David',89.60,85.26),
        (10,'Daniel',148.20,137.62),(11,'RyanC',174.86,125.38),(12,'Kyle',124.60,131.67),
        (13,'PatrickF',114.38,104.35),(14,'Kyle2',95.03,106.71),(15,'Raj',157.07,139.37),
    ],
    'Jeremy': [
        (1,'PatrickF',113.93,129.00),(2,'David',121.82,122.05),(3,'Kyle2',150.71,114.74),
        (4,'Daniel',124.23,122.57),(5,'Raj',126.71,172.15),(6,'RyanC',98.26,129.56),
        (7,'Ryan',109.77,155.52),(8,'Kyle',91.99,119.85),(9,'duncan',94.38,95.57),
        (10,'PatrickF',127.77,92.43),(11,'David',144.81,84.88),(12,'Kyle2',131.61,110.75),
        (13,'Daniel',164.11,124.95),(14,'Raj',138.87,139.72),(15,'RyanC',93.13,89.44),
    ],
}

# Playoffs 2021:
# Championship: SF1 Ryan vs David (seed1 vs 4), SF2 Duncan vs Kyle (seed2 vs 3)
# Consolation (wk17 only): 5th/6th Kyle2 vs Raj, 7th/8th Jeremy vs RyanC
# Teams 9th(Daniel) and 10th(PatrickF) had no playoff games
PLAYOFFS_2021 = [
    (16, 'Ryan',    'David',   139.73, 79.51,  True),   # SF1, Ryan wins
    (16, 'duncan',  'Kyle',    108.74, 182.57, True),   # SF2, Kyle wins (upset)
    (17, 'Ryan',    'Kyle',    125.64, 113.64, True),   # Final, Ryan champion
    (17, 'David',   'duncan',  161.85, 113.00, True),   # 3rd place, David wins
    (17, 'Kyle2',   'Raj',     121.58, 97.22,  True),   # 5th/6th, Kyle2 wins
    (17, 'Jeremy',  'RyanC',   124.74, 111.98, True),   # 7th/8th, Jeremy wins
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
print(f"Parsed {total_pairs} pairs, {total_games} games from report")

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

# Collect 2021 games
games = defaultdict(list)
seen  = set()

for mgr, schedule in SCHED_2021.items():
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

for (wk, m1, m2, s1, s2, is_po) in PLAYOFFS_2021:
    outer, inner = (m1, m2) if m1 < m2 else (m2, m1)
    if m1 < m2:
        games[(outer, inner)].append((s1, s2, is_po))
    else:
        games[(outer, inner)].append((s2, s1, is_po))

total_new = sum(len(v) for v in games.values())
print(f"2021 games: {total_new} (expect 75 reg-season + 6 playoff = 81; but 10 teams×9opponents×15/9wks...)")
# Actually: 10 teams, each plays 15 games, total = 10×15/2 = 75 unique reg-season games ✓
# Plus 6 playoff games = 81

# Merge
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
        if entry['last'] is None:
            winner = outer if s_outer > s_inner else inner
            entry['last'] = {'winner': winner, 'score1': s_outer,
                             'score2': s_inner, 'season': '21'}

# Write h2h_all.js
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
        lines.append(f"    '{inner}': {{w1:{e['w1']},w2:{e['w2']},"
                     f"pf1:{e['pf1']:.2f},pf2:{e['pf2']:.2f},"
                     f"big1:{b1},big2:{b2},last:{last_str},"
                     f"playoffs:{e['playoffs']},seasons:{e['seasons']}}}{comma}")
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
for a, b in [('Kyle','Kyle2'),('Ryan','Kyle'),('David','duncan')]:
    outer, inner = (a,b) if a<b else (b,a)
    e = existing.get(outer,{}).get(inner,{})
    print(f"  {outer} vs {inner}: w1={e.get('w1')},w2={e.get('w2')},seasons={e.get('seasons')},po={e.get('playoffs')}")
