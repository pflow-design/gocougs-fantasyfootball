import re
from collections import defaultdict

# 2016 mapping:
# 1:RogersGoodell→duncan, 2:DakInABox→David, 3:RussellAndFlow→Antony
# 4:Larson→Larson, 5:MyBallZachErtz→Daniel, 6:RussellSprouts→RyanC
# 7:ShmeyMaker→Raj, 8:SwingYourSword→Kyle, 9:TheGloriaHole→PatrickF, 10:ChalupaBatman→Kyle2
# Final standings: 1=Antony, 2=Kyle, 3=Raj, 4=RyanC, 5=Daniel, 6=Larson, 7=David, 8=duncan
#                  9=PatrickF, 10=Kyle2 (no playoffs)

SCHED_2016 = {
    'duncan': [
        (1,'David',102.99,113.35),(2,'Antony',92.86,113.77),(3,'Larson',74.51,129.55),
        (4,'Daniel',152.77,86.79),(5,'RyanC',117.25,133.01),(6,'Raj',153.90,75.23),
        (7,'Kyle',116.55,129.91),(8,'PatrickF',154.07,145.10),(9,'Kyle2',122.57,126.88),
        (10,'David',116.41,98.59),(11,'Antony',126.67,132.81),(12,'Larson',114.63,137.23),
        (13,'Daniel',107.49,135.21),(14,'RyanC',107.77,83.68),
    ],
    'David': [
        (1,'duncan',113.35,102.99),(2,'Kyle2',111.53,136.23),(3,'Antony',142.67,133.08),
        (4,'Larson',96.46,81.44),(5,'Daniel',97.59,107.35),(6,'RyanC',134.51,84.82),
        (7,'Raj',118.30,134.01),(8,'Kyle',115.65,110.47),(9,'PatrickF',129.93,96.47),
        (10,'duncan',98.59,116.41),(11,'Kyle2',121.54,76.44),(12,'Antony',117.60,124.04),
        (13,'Larson',84.89,117.14),(14,'Daniel',83.64,105.57),
    ],
    'Antony': [
        (1,'PatrickF',125.02,122.36),(2,'duncan',113.77,92.86),(3,'David',133.08,142.67),
        (4,'Kyle2',149.33,142.58),(5,'Larson',146.85,84.28),(6,'Daniel',105.11,86.38),
        (7,'RyanC',83.16,131.08),(8,'Raj',109.25,134.43),(9,'Kyle',65.42,79.86),
        (10,'PatrickF',132.66,103.54),(11,'duncan',132.81,126.67),(12,'David',124.04,117.60),
        (13,'Kyle2',161.33,82.65),(14,'Larson',143.23,90.66),
    ],
    'Larson': [
        (1,'Kyle',121.22,95.40),(2,'PatrickF',112.49,112.85),(3,'duncan',129.55,74.51),
        (4,'David',81.44,96.46),(5,'Antony',84.28,146.85),(6,'Kyle2',137.14,71.00),
        (7,'Daniel',101.25,118.45),(8,'RyanC',133.19,66.70),(9,'Raj',123.43,137.65),
        (10,'Kyle',118.32,136.87),(11,'PatrickF',100.50,80.65),(12,'duncan',137.23,114.63),
        (13,'David',117.14,84.89),(14,'Antony',90.66,143.23),
    ],
    'Daniel': [
        (1,'Raj',129.77,143.33),(2,'Kyle',140.95,108.42),(3,'PatrickF',92.95,90.55),
        (4,'duncan',86.79,152.77),(5,'David',107.35,97.59),(6,'Antony',86.38,105.11),
        (7,'Larson',118.45,101.25),(8,'Kyle2',116.85,88.79),(9,'RyanC',144.24,145.69),
        (10,'Raj',135.04,124.48),(11,'Kyle',75.84,100.29),(12,'PatrickF',125.64,110.02),
        (13,'duncan',135.21,107.49),(14,'David',105.57,83.64),
    ],
    'RyanC': [
        (1,'Kyle2',156.67,101.13),(2,'Raj',106.54,112.69),(3,'Kyle',130.78,120.06),
        (4,'PatrickF',140.80,144.22),(5,'duncan',133.01,117.25),(6,'David',134.51,84.82),
        (7,'Antony',131.08,83.16),(8,'Larson',66.70,133.19),(9,'Daniel',145.69,144.24),
        (10,'Kyle2',140.59,116.81),(11,'Raj',131.98,120.25),(12,'Kyle',100.54,114.74),
        (13,'PatrickF',131.16,86.31),(14,'duncan',83.68,107.77),
    ],
    'Raj': [
        (1,'Daniel',143.33,129.77),(2,'RyanC',112.69,106.54),(3,'Kyle2',157.90,93.73),
        (4,'Kyle',75.07,91.14),(5,'PatrickF',124.03,138.02),(6,'duncan',75.23,153.90),
        (7,'David',134.01,118.30),(8,'Antony',134.43,109.25),(9,'Larson',137.65,123.43),
        (10,'Daniel',124.48,135.04),(11,'RyanC',120.25,131.98),(12,'Kyle2',125.66,61.54),
        (13,'Kyle',92.79,132.27),(14,'PatrickF',84.21,66.11),
    ],
    'Kyle': [
        (1,'Larson',95.40,121.22),(2,'Daniel',108.42,140.95),(3,'RyanC',120.06,130.78),
        (4,'Raj',91.14,75.07),(5,'Kyle2',114.84,104.56),(6,'PatrickF',125.74,76.87),
        (7,'duncan',129.91,116.55),(8,'David',110.47,115.65),(9,'Antony',79.86,65.42),
        (10,'Larson',136.87,118.32),(11,'Daniel',100.29,75.84),(12,'RyanC',114.74,100.54),
        (13,'Raj',132.27,92.79),(14,'Kyle2',97.50,60.73),
    ],
    'PatrickF': [
        (1,'Antony',122.36,125.02),(2,'Larson',112.85,112.49),(3,'Daniel',90.55,92.95),
        (4,'RyanC',144.22,140.80),(5,'Raj',138.02,124.03),(6,'Kyle',76.87,125.74),
        (7,'Kyle2',79.51,140.03),(8,'duncan',145.10,154.07),(9,'David',96.47,129.93),
        (10,'Antony',103.54,132.66),(11,'Larson',80.65,100.50),(12,'Daniel',125.64,110.02),
        (13,'RyanC',86.31,131.16),(14,'Raj',66.11,84.21),
    ],
    'Kyle2': [
        (1,'RyanC',101.13,156.67),(2,'David',136.23,111.53),(3,'Raj',93.73,157.90),
        (4,'Antony',142.58,149.33),(5,'Kyle',104.56,114.84),(6,'Larson',71.00,137.14),
        (7,'PatrickF',140.03,79.51),(8,'Daniel',88.79,116.85),(9,'duncan',126.88,122.57),
        (10,'RyanC',116.81,140.59),(11,'David',76.44,121.54),(12,'Raj',61.54,125.66),
        (13,'Antony',82.65,161.33),(14,'Kyle',60.73,97.50),
    ],
}

# 2016 playoffs: SF wk15, Finals wk16 (single-week rounds)
# Seeds 1-4: Antony(1), Kyle(2), Raj(3), RyanC(4) → championship
# Seeds 5-8: Daniel(5), Larson(6), David(7), duncan(8) → consolation
# Seeds 9-10: PatrickF, Kyle2 → no playoffs
PLAYOFFS_2016 = [
    # Wk15 - Semifinals
    (15,'Antony','Raj',93.56,89.49,True),          # Antony wins SF
    (15,'Kyle','RyanC',144.07,78.50,True),         # Kyle wins SF
    # Wk15 - Consolation R1
    (15,'Daniel','duncan',156.79,97.15,True),      # Daniel wins
    (15,'Larson','David',131.69,109.19,True),      # Larson wins
    # Wk16 - Finals
    (16,'Antony','Kyle',140.54,89.51,True),        # Antony CHAMPION!
    (16,'Raj','RyanC',143.61,121.73,True),         # Raj wins 3rd
    # Wk16 - Consolation Finals
    (16,'Daniel','Larson',119.95,114.73,True),     # Daniel wins 5th
    (16,'David','duncan',142.34,88.50,True),       # David wins 7th
]

# ── Parse existing h2hData ───────────────────────────────────────────────────
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
    if om: cur_outer = om.group(1); existing[cur_outer] = {}; continue
    if cur_outer:
        m = entry_re.search(line)
        if m:
            existing[cur_outer][m.group(1)] = {
                'w1':int(m.group(2)),'w2':int(m.group(3)),
                'pf1':float(m.group(4)),'pf2':float(m.group(5)),
                'big1':None if m.group(6)=='null' else float(m.group(6)),
                'big2':None if m.group(7)=='null' else float(m.group(7)),
                'last':{'winner':m.group(8),'score1':float(m.group(9)),
                        'score2':float(m.group(10)),'season':m.group(11)},
                'playoffs':int(m.group(12)),'seasons':int(m.group(13))
            }
print(f"Parsed {sum(len(v) for v in existing.values())} pairs, "
      f"{sum(e['w1']+e['w2'] for d in existing.values() for e in d.values())} games")

def get_or_create(a, b):
    outer,inner = (a,b) if a<b else (b,a)
    if outer not in existing: existing[outer] = {}
    if inner not in existing[outer]:
        existing[outer][inner] = {'w1':0,'w2':0,'pf1':0.0,'pf2':0.0,
                                  'big1':None,'big2':None,'last':None,'playoffs':0,'seasons':0}
    return outer,inner,existing[outer][inner]

games = defaultdict(list)
seen = set()
for mgr, schedule in SCHED_2016.items():
    for (wk, opp, my_s, opp_s) in schedule:
        key = tuple(sorted([mgr, opp])) + (wk,)
        if key in seen: continue
        seen.add(key)
        outer,inner = (mgr,opp) if mgr<opp else (opp,mgr)
        if mgr<opp: games[(outer,inner)].append((my_s,opp_s,False))
        else:       games[(outer,inner)].append((opp_s,my_s,False))

for (wk,m1,m2,s1,s2,is_po) in PLAYOFFS_2016:
    key = tuple(sorted([m1,m2])) + (wk,)
    if key in seen: continue
    seen.add(key)
    outer,inner = (m1,m2) if m1<m2 else (m2,m1)
    if m1<m2: games[(outer,inner)].append((s1,s2,is_po))
    else:     games[(outer,inner)].append((s2,s1,is_po))

print(f"2016 games: {sum(len(v) for v in games.values())} (expect 70+8=78)")

seasons_added = set()
for (outer,inner),game_list in games.items():
    _,_,entry = get_or_create(outer, inner)
    if (outer,inner) not in seasons_added:
        entry['seasons'] += 1; seasons_added.add((outer,inner))
    for (s_outer, s_inner, is_po) in game_list:
        if s_outer > s_inner: entry['w1'] += 1
        else:                 entry['w2'] += 1
        entry['pf1'] = round(entry['pf1'] + s_outer, 2)
        entry['pf2'] = round(entry['pf2'] + s_inner, 2)
        if entry['big1'] is None or s_outer > entry['big1']: entry['big1'] = s_outer
        if entry['big2'] is None or s_inner > entry['big2']: entry['big2'] = s_inner
        if is_po: entry['playoffs'] += 1
        if entry['last'] is None:
            w = outer if s_outer > s_inner else inner
            entry['last'] = {'winner':w,'score1':s_outer,'score2':s_inner,'season':'16'}

lines = ['var h2hData = {']
for i,outer in enumerate(sorted(existing.keys())):
    lines.append(f"  '{outer}': {{")
    inner_items = list(existing[outer].items())
    for j,(inner,e) in enumerate(inner_items):
        last = e['last']
        ls = (f"{{winner:'{last['winner']}',score1:{last['score1']:.2f},"
              f"score2:{last['score2']:.2f},season:'{last['season']}'}}")
        b1 = f"{e['big1']:.2f}" if e['big1'] is not None else 'null'
        b2 = f"{e['big2']:.2f}" if e['big2'] is not None else 'null'
        c = '' if j==len(inner_items)-1 else ','
        lines.append(f"    '{inner}': {{w1:{e['w1']},w2:{e['w2']},"
                     f"pf1:{e['pf1']:.2f},pf2:{e['pf2']:.2f},"
                     f"big1:{b1},big2:{b2},last:{ls},"
                     f"playoffs:{e['playoffs']},seasons:{e['seasons']}}}{c}")
    c = '' if i==len(existing)-1 else ','
    lines.append(f"  }}{c}")
lines.append('};')
out = '\n'.join(lines)

with open('kdp_report.html') as f: html = f.read()
h2h_start = html.find('var h2hData = {'); h2h_end = html.find('\n};',h2h_start)+3
html_new = html[:h2h_start]+out+html[h2h_end:]
html_new = html_new.replace(
    'Data from 2017–2025 seasons · Historical seasons (2009–2016) compiling',
    'Data from 2016–2025 seasons · Historical seasons (2009–2015) compiling'
)
with open('kdp_report.html','w') as f: f.write(html_new)

total_p = sum(len(v) for v in existing.values())
total_g = sum(e['w1']+e['w2'] for d in existing.values() for e in d.values())
print(f"Done: {total_p} pairs, {total_g} total games")
# Spot check Antony champion (check Antony vs Kyle: Antony should lead)
for a,b in [('Antony','Kyle'),('Antony','Raj'),('Larson','PatrickF')]:
    outer,inner=(a,b) if a<b else (b,a)
    e=existing.get(outer,{}).get(inner,{})
    print(f"  {outer} vs {inner}: w1={e.get('w1')},w2={e.get('w2')},seasons={e.get('seasons')},po={e.get('playoffs')}")
