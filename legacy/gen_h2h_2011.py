import re
from collections import defaultdict

# 2011 mapping:
# 1=duncan, 2=PatrickF, 3=David, 4=Antony, 5=Bradley(1-season only!), 6=RyanC(Kibbles), 7=Larson(liverpoolsucks69)
# 8=Raj, 9=Daniel, 10=Kyle
# Note: Kyle2/Jeremy/Ryan not in league yet. Bradley only season.
# Seeds: Antony(1st,8-6), Kyle(2nd,10-4), Raj(3rd,11-3), Daniel(4th,8-6)
#        RyanC(5th,6-8), duncan(6th,7-7), Bradley(7th,6-8), David(8th,5-9)
# No playoffs: Larson(9th,5-9), PatrickF(10th,4-10)
# Final: 1=Antony(CHAMPION!), 2=Kyle, 3=Raj, 4=Daniel, 5=RyanC, 6=duncan, 7=Bradley, 8=David

SCHED_2011 = {
    'duncan': [
        (1,'PatrickF',123.54,107.20),(2,'David',150.08,100.69),(3,'Antony',131.40,120.09),
        (4,'Bradley',93.80,122.88),(5,'RyanC',91.33,112.03),(6,'Larson',111.45,108.21),
        (7,'Raj',70.04,127.64),(8,'Daniel',96.26,74.17),(9,'Kyle',131.95,138.72),
        (10,'PatrickF',121.38,90.26),(11,'David',106.99,111.81),(12,'Antony',107.40,116.92),
        (13,'Bradley',133.93,69.02),(14,'RyanC',138.05,157.33),
    ],
    'PatrickF': [
        (1,'duncan',107.20,123.54),(2,'Kyle',141.95,155.23),(3,'David',94.05,145.98),
        (4,'Antony',141.52,138.08),(5,'Bradley',91.66,161.27),(6,'RyanC',102.31,88.05),
        (7,'Larson',70.62,65.99),(8,'Raj',92.69,113.76),(9,'Daniel',136.33,106.23),
        (10,'duncan',90.26,121.38),(11,'Kyle',97.24,106.44),(12,'David',99.92,125.83),
        (13,'Antony',97.20,106.94),(14,'Bradley',110.60,124.67),
    ],
    'David': [
        (1,'Daniel',142.93,132.16),(2,'duncan',100.69,150.08),(3,'PatrickF',145.98,94.05),
        (4,'Kyle',125.53,110.00),(5,'Antony',89.18,132.21),(6,'Bradley',85.57,89.51),
        (7,'RyanC',118.94,133.27),(8,'Larson',117.64,117.83),(9,'Raj',107.56,119.12),
        (10,'Daniel',117.29,128.86),(11,'duncan',111.81,106.99),(12,'PatrickF',125.83,99.92),
        (13,'Kyle',125.30,164.05),(14,'Antony',78.78,134.10),
    ],
    'Antony': [
        (1,'Raj',101.83,114.75),(2,'Daniel',79.78,150.95),(3,'duncan',120.09,131.40),
        (4,'PatrickF',138.08,141.52),(5,'David',132.21,89.18),(6,'Kyle',105.63,115.62),
        (7,'Bradley',153.54,99.28),(8,'RyanC',113.56,129.62),(9,'Larson',89.80,78.58),
        (10,'Raj',93.33,86.61),(11,'Daniel',93.85,84.23),(12,'duncan',116.92,107.40),
        (13,'PatrickF',106.94,97.20),(14,'David',134.10,78.78),
    ],
    'Bradley': [
        (1,'Larson',96.76,122.38),(2,'Raj',160.90,161.43),(3,'Daniel',75.71,125.71),
        (4,'duncan',122.88,93.80),(5,'PatrickF',161.27,91.66),(6,'David',89.51,85.57),
        (7,'Antony',99.28,153.54),(8,'Kyle',148.80,97.88),(9,'RyanC',100.37,116.63),
        (10,'Larson',80.04,95.70),(11,'Raj',83.52,67.73),(12,'Daniel',84.17,140.02),
        (13,'duncan',69.02,133.93),(14,'PatrickF',124.67,110.60),
    ],
    'RyanC': [
        (1,'Kyle',103.66,129.50),(2,'Larson',77.16,129.71),(3,'Raj',94.22,130.83),
        (4,'Daniel',139.23,125.75),(5,'duncan',112.03,91.33),(6,'PatrickF',88.05,102.31),
        (7,'David',133.27,118.94),(8,'Antony',129.62,113.56),(9,'Bradley',116.63,100.37),
        (10,'Kyle',113.64,147.55),(11,'Larson',103.40,137.67),(12,'Raj',112.86,166.96),
        (13,'Daniel',130.20,154.19),(14,'duncan',157.33,138.05),
    ],
    'Larson': [
        (1,'Bradley',122.38,96.76),(2,'RyanC',129.71,77.16),(3,'Kyle',102.12,156.94),
        (4,'Raj',105.14,119.94),(5,'Daniel',73.03,151.64),(6,'duncan',108.21,111.45),
        (7,'PatrickF',65.99,70.62),(8,'David',117.83,117.64),(9,'Antony',78.58,89.80),
        (10,'Bradley',95.70,80.04),(11,'RyanC',137.67,103.40),(12,'Kyle',89.57,147.71),
        (13,'Raj',103.33,134.24),(14,'Daniel',98.95,143.68),
    ],
    'Raj': [
        (1,'Antony',114.75,101.83),(2,'Bradley',161.43,160.90),(3,'RyanC',130.83,94.22),
        (4,'Larson',119.94,105.14),(5,'Kyle',116.09,109.52),(6,'Daniel',127.92,97.45),
        (7,'duncan',127.64,70.04),(8,'PatrickF',113.76,92.69),(9,'David',119.12,107.56),
        (10,'Antony',86.61,93.33),(11,'Bradley',67.73,83.52),(12,'RyanC',166.96,112.86),
        (13,'Larson',134.24,103.33),(14,'Kyle',96.68,153.17),
    ],
    'Daniel': [
        (1,'David',132.16,142.93),(2,'Antony',150.95,79.78),(3,'Bradley',125.71,75.71),
        (4,'RyanC',125.75,139.23),(5,'Larson',151.64,73.03),(6,'Raj',97.45,127.92),
        (7,'Kyle',103.33,86.15),(8,'duncan',74.17,96.26),(9,'PatrickF',106.23,136.33),
        (10,'David',128.86,117.29),(11,'Antony',84.23,93.85),(12,'Bradley',140.02,84.17),
        (13,'RyanC',154.19,130.20),(14,'Larson',143.68,98.95),
    ],
    'Kyle': [
        (1,'RyanC',129.50,103.66),(2,'PatrickF',155.23,141.95),(3,'Larson',156.94,102.12),
        (4,'David',110.00,125.53),(5,'Raj',109.52,116.09),(6,'Antony',115.62,105.63),
        (7,'Daniel',86.15,103.33),(8,'Bradley',97.88,148.80),(9,'duncan',138.72,131.95),
        (10,'RyanC',147.55,113.64),(11,'PatrickF',106.44,97.24),(12,'Larson',147.71,89.57),
        (13,'David',164.05,125.30),(14,'Raj',153.17,96.68),
    ],
}

# Wk15 SF: Antony(1st) 153.49 vs Raj(3rd) 148.48 → Antony wins
#           Kyle(2nd) 126.36 vs Daniel(4th) 107.88 → Kyle wins
# Wk15 Consol: duncan(6th) 98.19 vs David(8th) 71.07 → duncan wins
#               RyanC(5th) 151.24 vs Bradley(7th) 101.49 → RyanC wins
# Wk16 Final: Antony 121.44 vs Kyle 91.13 → Antony CHAMPION!
# Wk16 3rd: Raj 155.58 vs Daniel 124.78 → Raj wins
# Wk16 5th: RyanC 146.44 vs duncan 145.69 → RyanC wins (by 0.75!)
# Wk16 7th: Bradley 84.80 vs David 64.01 → Bradley wins
PLAYOFFS_2011 = [
    (15,'Antony','Raj',153.49,148.48,True),
    (15,'Kyle','Daniel',126.36,107.88,True),
    (15,'duncan','David',98.19,71.07,True),
    (15,'RyanC','Bradley',151.24,101.49,True),
    (16,'Antony','Kyle',121.44,91.13,True),
    (16,'Raj','Daniel',155.58,124.78,True),
    (16,'RyanC','duncan',146.44,145.69,True),
    (16,'Bradley','David',84.80,64.01,True),
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
for mgr, schedule in SCHED_2011.items():
    for (wk, opp, my_s, opp_s) in schedule:
        key = tuple(sorted([mgr, opp])) + (wk,)
        if key in seen: continue
        seen.add(key)
        outer,inner = (mgr,opp) if mgr<opp else (opp,mgr)
        if mgr<opp: games[(outer,inner)].append((my_s,opp_s,False))
        else:       games[(outer,inner)].append((opp_s,my_s,False))

for (wk,m1,m2,s1,s2,is_po) in PLAYOFFS_2011:
    key = tuple(sorted([m1,m2])) + (wk,)
    if key in seen: continue
    seen.add(key)
    outer,inner = (m1,m2) if m1<m2 else (m2,m1)
    if m1<m2: games[(outer,inner)].append((s1,s2,is_po))
    else:     games[(outer,inner)].append((s2,s1,is_po))

print(f"2011 games: {sum(len(v) for v in games.values())} (expect 70+8=78)")

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
            entry['last'] = {'winner':w,'score1':s_outer,'score2':s_inner,'season':'11'}

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
    'Data from 2012–2025 seasons · Historical seasons (2009–2011) compiling',
    'Data from 2011–2025 seasons · Historical seasons (2009–2010) compiling'
)
with open('kdp_report.html','w') as f: f.write(html_new)

total_p = sum(len(v) for v in existing.values())
total_g = sum(e['w1']+e['w2'] for d in existing.values() for e in d.values())
print(f"Done: {total_p} pairs, {total_g} total games")
for a,b in [('Antony','Kyle'),('Antony','Raj'),('Bradley','duncan')]:
    outer,inner=(a,b) if a<b else (b,a)
    e=existing.get(outer,{}).get(inner,{})
    print(f"  {outer} vs {inner}: w1={e.get('w1')},w2={e.get('w2')},seasons={e.get('seasons')},po={e.get('playoffs')}")
