import re
from collections import defaultdict

# 2014 mapping:
# 1:MyMainThang→duncan, 2:CouginItMeansChamp!→David, 3:Larson→Larson
# 4:YourMom→Kyle2, 5:Ebner→Daniel, 6:HornsAndHalos→Antony
# 7:ShmeyMaker→Raj, 8:RussellSprouts→RyanC, 9:TheGloriaHole→PatrickF, 10:SwingYourSword→Kyle
# Seeds: 1=Antony, 2=Raj, 3=Daniel, 4=Larson, 5=Kyle2, 6=Kyle, 7=David, 8=PatrickF
# Final: 1=Antony(CHAMPION!), 2=Raj, 3=Daniel, 4=Larson, 5=Kyle2, 6=Kyle, 7=David, 8=PatrickF
# No playoffs: RyanC(9th), duncan(10th)

SCHED_2014 = {
    'duncan': [
        (1,'David',149.88,102.13),(2,'Larson',65.20,114.81),(3,'Kyle2',128.10,96.62),
        (4,'Daniel',116.61,133.84),(5,'Antony',74.71,146.91),(6,'Raj',97.15,141.21),
        (7,'RyanC',83.14,124.84),(8,'PatrickF',142.56,172.04),(9,'Kyle',102.55,131.07),
        (10,'David',101.23,173.74),(11,'Larson',117.80,87.31),(12,'Kyle2',155.84,122.89),
        (13,'Daniel',140.77,112.32),(14,'Antony',146.01,153.13),
    ],
    'David': [
        (1,'duncan',102.13,149.88),(2,'Kyle',119.31,145.87),(3,'Larson',88.49,128.53),
        (4,'Kyle2',156.30,78.69),(5,'Daniel',114.76,90.51),(6,'Antony',92.84,152.84),
        (7,'Raj',119.18,141.86),(8,'RyanC',125.91,172.76),(9,'PatrickF',122.82,136.80),
        (10,'duncan',173.74,101.23),(11,'Kyle',99.26,88.15),(12,'Larson',114.87,97.35),
        (13,'Kyle2',94.22,71.39),(14,'Daniel',69.03,159.31),
    ],
    'Larson': [
        (1,'PatrickF',109.10,91.39),(2,'duncan',114.81,65.20),(3,'David',128.53,88.49),
        (4,'Kyle',107.37,103.58),(5,'Kyle2',87.92,134.41),(6,'Daniel',126.02,107.26),
        (7,'Antony',98.00,115.47),(8,'Raj',118.16,101.99),(9,'RyanC',87.20,111.59),
        (10,'PatrickF',131.74,105.59),(11,'duncan',87.31,117.80),(12,'David',97.35,114.87),
        (13,'Kyle',126.27,196.20),(14,'Kyle2',162.60,106.83),
    ],
    'Kyle2': [
        (1,'RyanC',123.30,92.36),(2,'PatrickF',115.98,133.65),(3,'duncan',96.62,128.10),
        (4,'David',78.69,156.30),(5,'Larson',134.41,87.92),(6,'Kyle',139.10,127.97),
        (7,'Daniel',114.90,101.67),(8,'Antony',150.03,141.05),(9,'Raj',129.95,148.12),
        (10,'RyanC',121.74,86.50),(11,'PatrickF',126.15,73.53),(12,'duncan',122.89,155.84),
        (13,'David',71.39,94.22),(14,'Larson',106.83,162.60),
    ],
    'Daniel': [
        (1,'Raj',89.12,119.23),(2,'RyanC',116.34,75.39),(3,'PatrickF',91.29,90.55),
        (4,'duncan',133.84,116.61),(5,'David',90.51,114.76),(6,'Larson',107.26,126.02),
        (7,'Kyle2',101.67,114.90),(8,'Kyle',115.29,99.77),(9,'Antony',135.22,89.52),
        (10,'Raj',151.43,145.07),(11,'RyanC',131.17,105.54),(12,'PatrickF',91.42,169.53),
        (13,'duncan',112.32,140.77),(14,'David',159.31,69.03),
    ],
    'Antony': [
        (1,'Kyle',126.20,130.02),(2,'Raj',116.09,114.45),(3,'RyanC',134.77,73.46),
        (4,'PatrickF',96.15,137.70),(5,'duncan',146.91,74.71),(6,'David',152.84,92.84),
        (7,'Larson',115.47,98.00),(8,'Kyle2',141.05,150.03),(9,'Daniel',89.52,135.22),
        (10,'Kyle',114.45,81.61),(11,'Raj',99.05,103.95),(12,'RyanC',132.90,124.40),
        (13,'PatrickF',148.55,145.32),(14,'duncan',153.13,146.01),
    ],
    'Raj': [
        (1,'Daniel',119.23,89.12),(2,'Antony',114.45,116.09),(3,'Kyle',111.66,107.24),
        (4,'RyanC',118.95,136.91),(5,'PatrickF',157.78,123.34),(6,'duncan',141.21,97.15),
        (7,'David',141.86,119.18),(8,'Larson',101.99,118.16),(9,'Kyle2',148.12,129.95),
        (10,'Daniel',145.07,151.43),(11,'Antony',103.95,99.05),(12,'Kyle',155.91,86.47),
        (13,'RyanC',148.20,124.80),(14,'PatrickF',97.26,93.23),
    ],
    'RyanC': [
        (1,'Kyle2',92.36,123.30),(2,'Daniel',75.39,116.34),(3,'Antony',73.46,134.77),
        (4,'Raj',136.91,118.95),(5,'Kyle',117.11,103.47),(6,'PatrickF',90.53,103.28),
        (7,'duncan',124.84,83.14),(8,'David',172.76,125.91),(9,'Larson',111.59,87.20),
        (10,'Kyle2',86.50,121.74),(11,'Daniel',105.54,131.17),(12,'Antony',124.40,132.90),
        (13,'Raj',124.80,148.20),(14,'Kyle',120.98,188.87),
    ],
    'PatrickF': [
        (1,'Larson',91.39,109.10),(2,'Kyle2',133.65,115.98),(3,'Daniel',90.55,91.29),
        (4,'Antony',137.70,96.15),(5,'Raj',123.34,157.78),(6,'RyanC',103.28,90.53),
        (7,'Kyle',114.06,99.46),(8,'duncan',172.04,142.56),(9,'David',136.80,122.82),
        (10,'Larson',105.59,131.74),(11,'Kyle2',73.53,126.15),(12,'Daniel',169.53,91.42),
        (13,'Antony',145.32,148.55),(14,'Raj',93.23,97.26),
    ],
    'Kyle': [
        (1,'Antony',130.02,126.20),(2,'David',145.87,119.31),(3,'Raj',107.24,111.66),
        (4,'Larson',103.58,107.37),(5,'RyanC',103.47,117.11),(6,'Kyle2',127.97,139.10),
        (7,'PatrickF',99.46,114.06),(8,'Daniel',99.77,115.29),(9,'duncan',131.07,102.55),
        (10,'Antony',81.61,114.45),(11,'David',88.15,99.26),(12,'Raj',86.47,155.91),
        (13,'Larson',196.20,126.27),(14,'RyanC',188.87,120.98),
    ],
}

# 2014 playoffs: SF wk15, Finals wk16
# Seeds 1-4: Antony(1st), Raj(2nd), Daniel(3rd), Larson(4th)
# Seeds 5-8: Kyle2(5th), Kyle(6th), David(7th), PatrickF(8th)
# No playoffs: RyanC(9th), duncan(10th)
PLAYOFFS_2014 = [
    # Wk15 SF
    (15,'Raj','Larson',142.95,71.79,True),        # Raj wins SF
    (15,'Antony','Daniel',116.84,104.14,True),    # Antony wins SF
    # Wk15 Consolation R1
    (15,'Kyle','PatrickF',109.12,102.20,True),    # Kyle wins
    (15,'Kyle2','David',91.48,76.12,True),        # Kyle2 wins
    # Wk16 Final
    (16,'Antony','Raj',155.31,87.84,True),        # Antony CHAMPION!
    (16,'Daniel','Larson',142.92,115.60,True),    # Daniel wins 3rd
    # Wk16 Consolation Finals
    (16,'Kyle2','Kyle',105.02,83.90,True),        # Kyle2 wins 5th
    (16,'David','PatrickF',91.64,73.65,True),     # David wins 7th
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
for mgr, schedule in SCHED_2014.items():
    for (wk, opp, my_s, opp_s) in schedule:
        key = tuple(sorted([mgr, opp])) + (wk,)
        if key in seen: continue
        seen.add(key)
        outer,inner = (mgr,opp) if mgr<opp else (opp,mgr)
        if mgr<opp: games[(outer,inner)].append((my_s,opp_s,False))
        else:       games[(outer,inner)].append((opp_s,my_s,False))

for (wk,m1,m2,s1,s2,is_po) in PLAYOFFS_2014:
    key = tuple(sorted([m1,m2])) + (wk,)
    if key in seen: continue
    seen.add(key)
    outer,inner = (m1,m2) if m1<m2 else (m2,m1)
    if m1<m2: games[(outer,inner)].append((s1,s2,is_po))
    else:     games[(outer,inner)].append((s2,s1,is_po))

print(f"2014 games: {sum(len(v) for v in games.values())} (expect 70+8=78)")

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
            entry['last'] = {'winner':w,'score1':s_outer,'score2':s_inner,'season':'14'}

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
    'Data from 2015–2025 seasons · Historical seasons (2009–2014) compiling',
    'Data from 2014–2025 seasons · Historical seasons (2009–2013) compiling'
)
with open('kdp_report.html','w') as f: f.write(html_new)

total_p = sum(len(v) for v in existing.values())
total_g = sum(e['w1']+e['w2'] for d in existing.values() for e in d.values())
print(f"Done: {total_p} pairs, {total_g} total games")
for a,b in [('Antony','Raj'),('Larson','Raj'),('Kyle2','Kyle')]:
    outer,inner=(a,b) if a<b else (b,a)
    e=existing.get(outer,{}).get(inner,{})
    print(f"  {outer} vs {inner}: w1={e.get('w1')},w2={e.get('w2')},seasons={e.get('seasons')},po={e.get('playoffs')}")
