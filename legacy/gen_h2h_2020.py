import re
from collections import defaultdict

# 2020 team mapping:
# 1:Candyman→duncan, 2:WokeUpFeelinDangaRus→David, 3:Clappin'Cheeks→Jeremy
# 4:MyBallZachErtz→Daniel, 5:RussellSprouts→RyanC, 6:RollinWithRolovich→Kyle
# 7:DicksonYourFace→PatrickF, 8:TheCovid-19's→Kyle2, 9:shneyMaker→Raj, 10:PlayDaktion→Ryan

SCHED_2020 = {
    'duncan': [
        (1,'David',100.63,140.11),(2,'Jeremy',117.62,91.94),(3,'Daniel',139.04,123.65),
        (4,'RyanC',101.73,117.73),(5,'Kyle',107.24,133.01),(6,'PatrickF',134.54,106.29),
        (7,'Kyle2',68.45,61.10),(8,'Raj',127.65,99.39),(9,'Ryan',104.70,122.40),
        (10,'David',68.33,127.05),(11,'Jeremy',105.58,126.83),(12,'Daniel',134.00,148.92),
        (13,'RyanC',109.95,129.62),(14,'Kyle',110.62,120.10),
    ],
    'David': [
        (1,'duncan',140.11,100.63),(2,'Ryan',182.78,100.97),(3,'Jeremy',163.84,113.44),
        (4,'Daniel',168.43,124.87),(5,'RyanC',138.37,103.04),(6,'Kyle',95.57,79.48),
        (7,'PatrickF',148.28,111.48),(8,'Kyle2',143.07,109.31),(9,'Raj',101.40,126.82),
        (10,'duncan',127.05,68.33),(11,'Ryan',109.02,100.76),(12,'Jeremy',100.95,81.27),
        (13,'Daniel',138.09,111.80),(14,'RyanC',151.81,89.01),
    ],
    'Jeremy': [
        (1,'Raj',145.66,101.56),(2,'duncan',91.94,117.62),(3,'David',113.44,163.84),
        (4,'Ryan',148.92,172.60),(5,'Daniel',104.89,176.59),(6,'RyanC',96.67,107.91),
        (7,'Kyle',143.53,104.21),(8,'PatrickF',108.22,109.59),(9,'Kyle2',123.36,106.21),
        (10,'Raj',87.42,116.20),(11,'duncan',126.83,105.58),(12,'David',81.27,100.95),
        (13,'Ryan',145.64,104.66),(14,'Daniel',145.28,130.10),
    ],
    'Daniel': [
        (1,'Kyle2',132.29,103.84),(2,'Raj',141.93,135.55),(3,'duncan',123.65,139.04),
        (4,'David',124.87,168.43),(5,'Jeremy',176.59,104.89),(6,'Ryan',150.73,111.31),
        (7,'RyanC',163.26,82.82),(8,'Kyle',96.21,94.85),(9,'PatrickF',94.64,84.41),
        (10,'Kyle2',101.06,98.86),(11,'Raj',140.82,155.93),(12,'duncan',148.92,134.00),
        (13,'David',111.80,138.09),(14,'Jeremy',130.10,145.28),
    ],
    'RyanC': [
        (1,'PatrickF',125.57,136.84),(2,'Kyle2',106.45,150.38),(3,'Raj',131.25,146.27),
        (4,'duncan',117.73,101.73),(5,'David',103.04,138.37),(6,'Jeremy',107.91,96.67),
        (7,'Daniel',82.82,163.26),(8,'Ryan',152.56,70.76),(9,'Kyle',102.40,141.34),
        (10,'PatrickF',107.60,127.61),(11,'Kyle2',117.61,84.02),(12,'Raj',113.52,123.89),
        (13,'duncan',129.62,109.95),(14,'David',89.01,151.81),
    ],
    'Kyle': [
        (1,'Ryan',147.04,98.97),(2,'PatrickF',118.86,125.42),(3,'Kyle2',94.30,146.59),
        (4,'Raj',82.58,89.85),(5,'duncan',133.01,107.24),(6,'David',79.48,95.57),
        (7,'Jeremy',104.21,143.53),(8,'Daniel',94.85,96.21),(9,'RyanC',141.34,102.40),
        (10,'Ryan',80.27,128.03),(11,'PatrickF',110.73,114.64),(12,'Kyle2',89.93,154.32),
        (13,'Raj',91.71,126.25),(14,'duncan',120.10,110.62),
    ],
    'PatrickF': [
        (1,'RyanC',136.84,125.57),(2,'Kyle',125.42,118.86),(3,'Ryan',131.55,126.91),
        (4,'Kyle2',90.67,137.40),(5,'Raj',136.57,115.09),(6,'duncan',106.29,134.54),
        (7,'David',111.48,148.28),(8,'Jeremy',109.59,108.22),(9,'Daniel',84.41,94.64),
        (10,'RyanC',127.61,107.60),(11,'Kyle',114.64,110.73),(12,'Ryan',87.21,120.65),
        (13,'Kyle2',85.36,130.22),(14,'Raj',117.66,125.43),
    ],
    'Kyle2': [
        (1,'Daniel',103.84,132.29),(2,'RyanC',150.38,106.45),(3,'Kyle',146.59,94.30),
        (4,'PatrickF',137.40,90.67),(5,'Ryan',105.39,87.61),(6,'Raj',90.39,153.46),
        (7,'duncan',61.10,68.45),(8,'David',109.31,143.07),(9,'Jeremy',106.21,123.36),
        (10,'Daniel',98.86,101.06),(11,'RyanC',84.02,117.61),(12,'Kyle',154.32,89.93),
        (13,'PatrickF',130.22,85.36),(14,'Ryan',113.63,99.32),
    ],
    'Raj': [
        (1,'Jeremy',101.56,145.66),(2,'Daniel',135.55,141.93),(3,'RyanC',146.27,131.25),
        (4,'Kyle',89.85,82.58),(5,'PatrickF',115.09,136.57),(6,'Kyle2',153.46,90.39),
        (7,'Ryan',157.10,133.71),(8,'duncan',99.39,127.65),(9,'David',126.82,101.40),
        (10,'Jeremy',116.20,87.42),(11,'Daniel',155.93,140.82),(12,'RyanC',123.89,113.52),
        (13,'Kyle',126.25,91.71),(14,'PatrickF',125.43,117.66),
    ],
    'Ryan': [
        (1,'Kyle',98.97,147.04),(2,'David',100.97,182.78),(3,'PatrickF',126.91,131.55),
        (4,'Jeremy',172.60,148.92),(5,'Kyle2',87.61,105.39),(6,'Daniel',111.31,150.73),
        (7,'Raj',133.71,157.10),(8,'RyanC',70.76,152.56),(9,'duncan',122.40,104.70),
        (10,'Kyle',128.03,80.27),(11,'David',100.76,109.02),(12,'PatrickF',120.65,87.21),
        (13,'Jeremy',104.66,145.64),(14,'Kyle2',99.32,113.63),
    ],
}

# Playoffs 2020 (wk15=SF, wk16=Final/3rd/consolation)
# Championship: seed1=David, seed2=Raj, seed3=Daniel, seed4=Kyle2
# Consolation (wk16 only): 5th/6th RyanC vs PatrickF, 7th/8th Jeremy vs Duncan
# Kyle and Ryan had no playoff games
PLAYOFFS_2020 = [
    (15,'David','Kyle2',134.91,113.45,True),   # SF1, David wins
    (15,'Raj','Daniel',129.41,141.58,True),     # SF2, Daniel wins (upset)
    (16,'David','Daniel',178.14,125.26,True),   # Final, David champion
    (16,'Raj','Kyle2',103.81,128.35,True),      # 3rd place, Kyle2 wins
    (16,'RyanC','PatrickF',138.38,109.49,True), # 5th/6th, RyanC wins
    (16,'Jeremy','duncan',111.14,106.59,True),  # 7th/8th, Jeremy wins
]

# ── PARSE EXISTING h2hData FROM kdp_report.html ──────────────────────────────
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

print(f"Parsed {sum(len(v) for v in existing.values())} pairs, "
      f"{sum(e['w1']+e['w2'] for d in existing.values() for e in d.values())} games")

def get_or_create(a, b):
    outer, inner = (a, b) if a < b else (b, a)
    if outer not in existing:
        existing[outer] = {}
    if inner not in existing[outer]:
        existing[outer][inner] = {
            'w1':0,'w2':0,'pf1':0.0,'pf2':0.0,
            'big1':None,'big2':None,'last':None,'playoffs':0,'seasons':0
        }
    return outer, inner, existing[outer][inner]

games = defaultdict(list)
seen  = set()

for mgr, schedule in SCHED_2020.items():
    for (wk, opp, my_s, opp_s) in schedule:
        key = tuple(sorted([mgr, opp])) + (wk,)
        if key in seen: continue
        seen.add(key)
        outer, inner = (mgr, opp) if mgr < opp else (opp, mgr)
        if mgr < opp:
            games[(outer,inner)].append((my_s, opp_s, False))
        else:
            games[(outer,inner)].append((opp_s, my_s, False))

for (wk,m1,m2,s1,s2,is_po) in PLAYOFFS_2020:
    outer, inner = (m1,m2) if m1<m2 else (m2,m1)
    if m1<m2: games[(outer,inner)].append((s1,s2,is_po))
    else:     games[(outer,inner)].append((s2,s1,is_po))

total_new = sum(len(v) for v in games.values())
print(f"2020 games: {total_new} (expect 10*14/2=70 reg + 6 playoff = 76)")

seasons_added = set()
for (outer, inner), game_list in games.items():
    _, _, entry = get_or_create(outer, inner)
    if (outer,inner) not in seasons_added:
        entry['seasons'] += 1
        seasons_added.add((outer,inner))
    for (s_outer, s_inner, is_po) in game_list:
        if s_outer > s_inner: entry['w1'] += 1
        else:                 entry['w2'] += 1
        entry['pf1'] = round(entry['pf1'] + s_outer, 2)
        entry['pf2'] = round(entry['pf2'] + s_inner, 2)
        if entry['big1'] is None or s_outer > entry['big1']: entry['big1'] = s_outer
        if entry['big2'] is None or s_inner > entry['big2']: entry['big2'] = s_inner
        if is_po: entry['playoffs'] += 1
        if entry['last'] is None:
            winner = outer if s_outer > s_inner else inner
            entry['last'] = {'winner':winner,'score1':s_outer,'score2':s_inner,'season':'20'}

# Write h2h_all.js
lines = ['var h2hData = {']
for i, outer in enumerate(sorted(existing.keys())):
    lines.append(f"  '{outer}': {{")
    inner_items = list(existing[outer].items())
    for j, (inner, e) in enumerate(inner_items):
        last = e['last']
        last_str = (f"{{winner:'{last['winner']}',score1:{last['score1']:.2f},"
                    f"score2:{last['score2']:.2f},season:'{last['season']}'}}")
        b1 = f"{e['big1']:.2f}" if e['big1'] is not None else 'null'
        b2 = f"{e['big2']:.2f}" if e['big2'] is not None else 'null'
        comma = '' if j==len(inner_items)-1 else ','
        lines.append(f"    '{inner}': {{w1:{e['w1']},w2:{e['w2']},"
                     f"pf1:{e['pf1']:.2f},pf2:{e['pf2']:.2f},"
                     f"big1:{b1},big2:{b2},last:{last_str},"
                     f"playoffs:{e['playoffs']},seasons:{e['seasons']}}}{comma}")
    comma = '' if i==len(existing)-1 else ','
    lines.append(f"  }}{comma}")
lines.append('};')

out = '\n'.join(lines)
with open('h2h_all.js','w') as f:
    f.write(out)
# Inject into report
with open('kdp_report.html') as f:
    html = f.read()
h2h_start = html.find('var h2hData = {')
h2h_end   = html.find('\n};', h2h_start) + 3
html_new = html[:h2h_start] + out + html[h2h_end:]
html_new = html_new.replace(
    'Data from 2021–2025 seasons · Historical seasons (2009–2020) compiling',
    'Data from 2020–2025 seasons · Historical seasons (2009–2019) compiling'
)
with open('kdp_report.html','w') as f:
    f.write(html_new)

total_p = sum(len(v) for v in existing.values())
total_g = sum(e['w1']+e['w2'] for d in existing.values() for e in d.values())
print(f"Done: {total_p} pairs, {total_g} total games")
# Spot checks
for a,b in [('David','Kyle2'),('Ryan','david'),('David','Raj')]:
    b2 = b if b[0].isupper() else b
    outer,inner = (a,b2) if a<b2 else (b2,a)
    e = existing.get(outer,{}).get(inner,{})
    print(f"  {outer} vs {inner}: w1={e.get('w1')},w2={e.get('w2')},seasons={e.get('seasons')},po={e.get('playoffs')}")
