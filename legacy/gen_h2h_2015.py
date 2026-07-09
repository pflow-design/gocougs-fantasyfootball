import re
from collections import defaultdict

# 2015 mapping:
# 1:MyMainThang→duncan, 2:Larson→Larson, 3:KingDomeRafters→Antony
# 4:CouginItMeansChamp!→David, 5:MyBallZachErtz→Daniel, 6:YourMom→Kyle2
# 7:TheGloriaHole→PatrickF, 8:RussellSprouts→RyanC, 9:SwingYourSword→Kyle, 10:ShmeyMaker→Raj
# Final: 1=PatrickF(CHAMPION!), 2=Daniel, 3=Raj, 4=RyanC
#         5=Kyle2, 6=Larson, 7=Antony, 8=Kyle, 9=duncan, 10=David

SCHED_2015 = {
    'duncan': [
        (1,'Larson',114.94,82.47),(2,'Antony',95.80,112.40),(3,'David',152.57,187.44),
        (4,'Daniel',91.88,108.73),(5,'Kyle2',94.84,130.54),(6,'PatrickF',165.74,90.84),
        (7,'RyanC',114.75,112.20),(8,'Kyle',89.84,104.35),(9,'Raj',117.13,125.49),
        (10,'Larson',99.94,91.27),(11,'Antony',107.86,70.99),(12,'David',128.17,137.96),
        (13,'Daniel',77.86,155.45),(14,'Kyle2',72.70,82.27),
    ],
    'Larson': [
        (1,'duncan',82.47,114.94),(2,'Raj',89.97,132.56),(3,'Antony',125.93,115.59),
        (4,'David',100.75,78.74),(5,'Daniel',97.64,124.88),(6,'Kyle2',87.34,150.57),
        (7,'PatrickF',79.07,119.10),(8,'RyanC',132.24,116.98),(9,'Kyle',110.77,65.23),
        (10,'duncan',91.27,99.94),(11,'Raj',94.73,92.01),(12,'Antony',150.50,130.26),
        (13,'David',135.29,141.50),(14,'Daniel',132.65,103.05),
    ],
    'Antony': [
        (1,'Kyle',123.29,140.91),(2,'duncan',112.40,95.80),(3,'Larson',115.59,125.93),
        (4,'Raj',89.92,120.92),(5,'David',108.86,100.31),(6,'Daniel',109.09,98.33),
        (7,'Kyle2',168.46,112.50),(8,'PatrickF',124.84,159.03),(9,'RyanC',151.79,171.38),
        (10,'Kyle',117.98,98.71),(11,'duncan',70.99,107.86),(12,'Larson',130.26,150.50),
        (13,'Raj',113.85,75.61),(14,'David',141.60,131.76),
    ],
    'David': [
        (1,'RyanC',118.43,173.72),(2,'Kyle',102.36,118.75),(3,'duncan',187.44,152.57),
        (4,'Larson',100.75,78.74),(5,'Antony',100.31,108.86),(6,'Raj',118.79,139.15),
        (7,'Daniel',111.07,127.24),(8,'Kyle2',85.91,104.27),(9,'PatrickF',117.26,136.77),
        (10,'RyanC',80.01,133.54),(11,'Kyle',92.83,112.76),(12,'duncan',137.96,128.17),
        (13,'Larson',141.50,135.29),(14,'Antony',131.76,141.60),
    ],
    'Daniel': [
        (1,'PatrickF',102.14,144.96),(2,'RyanC',89.73,123.85),(3,'Kyle',146.49,66.78),
        (4,'duncan',108.73,91.88),(5,'Larson',124.88,97.64),(6,'Antony',98.33,109.09),
        (7,'David',127.24,111.07),(8,'Raj',128.22,120.95),(9,'Kyle2',149.64,108.75),
        (10,'PatrickF',143.06,72.42),(11,'RyanC',123.91,108.57),(12,'Kyle',95.25,119.74),
        (13,'duncan',155.45,77.86),(14,'Larson',103.05,132.65),
    ],
    'Kyle2': [
        (1,'Raj',118.25,110.18),(2,'PatrickF',78.70,109.86),(3,'RyanC',117.34,139.88),
        (4,'Kyle',109.41,134.66),(5,'duncan',130.54,94.84),(6,'Larson',150.57,87.34),
        (7,'Antony',112.50,168.46),(8,'David',104.27,85.91),(9,'Daniel',108.75,149.64),
        (10,'Raj',53.97,113.78),(11,'PatrickF',85.05,99.44),(12,'RyanC',108.90,83.17),
        (13,'Kyle',136.00,125.87),(14,'duncan',82.27,72.70),
    ],
    'PatrickF': [
        (1,'Daniel',144.96,102.14),(2,'Kyle2',109.86,78.70),(3,'Raj',149.50,129.90),
        (4,'RyanC',104.65,97.97),(5,'Kyle',113.34,120.96),(6,'duncan',90.84,165.74),
        (7,'Larson',119.10,79.07),(8,'Antony',159.03,124.84),(9,'David',136.77,117.26),
        (10,'Daniel',72.42,143.06),(11,'Kyle2',99.44,85.05),(12,'Raj',75.22,96.42),
        (13,'RyanC',121.54,170.93),(14,'Kyle',115.08,102.95),
    ],
    'RyanC': [
        (1,'David',173.72,118.43),(2,'Daniel',123.85,89.73),(3,'Kyle2',139.88,117.34),
        (4,'PatrickF',97.97,104.65),(5,'Raj',116.49,102.64),(6,'Kyle',133.20,119.23),
        (7,'duncan',112.20,114.75),(8,'Larson',116.98,132.24),(9,'Antony',171.38,151.79),
        (10,'David',133.54,80.01),(11,'Daniel',108.57,123.91),(12,'Kyle2',83.17,108.90),
        (13,'PatrickF',121.54,170.93),(14,'Raj',92.92,136.76),
    ],
    'Kyle': [
        (1,'Antony',140.91,123.29),(2,'David',118.75,102.36),(3,'Daniel',66.78,146.49),
        (4,'Kyle2',134.66,109.41),(5,'PatrickF',120.96,113.34),(6,'RyanC',119.23,133.20),
        (7,'Raj',128.94,151.18),(8,'duncan',104.35,89.84),(9,'Larson',65.23,110.77),
        (10,'Antony',98.71,117.98),(11,'David',112.76,92.83),(12,'Daniel',119.74,95.25),
        (13,'Kyle2',125.87,136.00),(14,'PatrickF',102.95,115.08),
    ],
    'Raj': [
        (1,'Kyle2',110.18,118.25),(2,'Larson',132.56,89.97),(3,'PatrickF',129.90,149.50),
        (4,'Antony',120.92,89.92),(5,'RyanC',102.64,116.49),(6,'David',139.15,118.79),
        (7,'Kyle',151.18,128.94),(8,'Daniel',120.95,128.22),(9,'duncan',125.49,117.13),
        (10,'Kyle2',113.78,53.97),(11,'Larson',92.01,94.73),(12,'PatrickF',96.42,75.22),
        (13,'Antony',75.61,113.85),(14,'RyanC',136.76,92.92),
    ],
}

# 2015 playoffs
# Seeds: 1=PatrickF, 2=Daniel, 3=Raj, 4=RyanC | 5=Kyle2, 6=Larson, 7=Antony, 8=Kyle
# 9=duncan, 10=David (no playoffs)
PLAYOFFS_2015 = [
    # Wk15 Championship Semifinals
    (15,'PatrickF','RyanC',161.37,155.50,True),    # PatrickF wins SF
    (15,'Daniel','Raj',123.80,121.43,True),         # Daniel wins SF
    # Wk15 Consolation R1
    (15,'Larson','Antony',157.57,136.02,True),      # Larson wins
    (15,'Kyle2','Kyle',107.66,82.63,True),           # Kyle2 wins
    # Wk16 Championship Final
    (16,'PatrickF','Daniel',88.05,74.24,True),      # PatrickF CHAMPION!
    (16,'Raj','RyanC',127.97,113.11,True),          # Raj wins 3rd
    # Wk16 Consolation Finals
    (16,'Kyle2','Larson',116.63,85.93,True),        # Kyle2 wins 5th
    (16,'Antony','Kyle',124.81,73.87,True),         # Antony wins 7th
]

# ── Parse and merge ──────────────────────────────────────────────────────────
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
for mgr, schedule in SCHED_2015.items():
    for (wk, opp, my_s, opp_s) in schedule:
        key = tuple(sorted([mgr, opp])) + (wk,)
        if key in seen: continue
        seen.add(key)
        outer,inner = (mgr,opp) if mgr<opp else (opp,mgr)
        if mgr<opp: games[(outer,inner)].append((my_s,opp_s,False))
        else:       games[(outer,inner)].append((opp_s,my_s,False))

for (wk,m1,m2,s1,s2,is_po) in PLAYOFFS_2015:
    key = tuple(sorted([m1,m2])) + (wk,)
    if key in seen: continue
    seen.add(key)
    outer,inner = (m1,m2) if m1<m2 else (m2,m1)
    if m1<m2: games[(outer,inner)].append((s1,s2,is_po))
    else:     games[(outer,inner)].append((s2,s1,is_po))

print(f"2015 games: {sum(len(v) for v in games.values())} (expect 70+8=78)")

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
            entry['last'] = {'winner':w,'score1':s_outer,'score2':s_inner,'season':'15'}

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
    'Data from 2016–2025 seasons · Historical seasons (2009–2015) compiling',
    'Data from 2015–2025 seasons · Historical seasons (2009–2014) compiling'
)
with open('kdp_report.html','w') as f: f.write(html_new)

total_p = sum(len(v) for v in existing.values())
total_g = sum(e['w1']+e['w2'] for d in existing.values() for e in d.values())
print(f"Done: {total_p} pairs, {total_g} total games")
for a,b in [('PatrickF','RyanC'),('Antony','Kyle2'),('Larson','RyanC')]:
    outer,inner=(a,b) if a<b else (b,a)
    e=existing.get(outer,{}).get(inner,{})
    print(f"  {outer} vs {inner}: w1={e.get('w1')},w2={e.get('w2')},seasons={e.get('seasons')},po={e.get('playoffs')}")
