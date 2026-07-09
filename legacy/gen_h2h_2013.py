import re
from collections import defaultdict

# 2013 mapping:
# 1=duncan, 2=PatrickF, 3=Larson, 4=Antony, 5=Daniel, 6=David, 7=Kyle2, 8=Raj, 9=RyanC, 10=Kyle
# Seeds: Larson(1st,10-4), duncan(2nd,9-5), Raj(3rd,11-3!), Kyle(4th,10-4)
#        RyanC(5th,6-8), Antony(6th,8-6), Daniel(7th,4-10), David(8th,7-7)
# No playoffs: Kyle2(2-12), PatrickF(3-11)
# Final: 1=Larson(CHAMPION!), 2=duncan, 3=Raj, 4=Kyle, 5=RyanC, 6=Antony, 7=Daniel, 8=David

SCHED_2013 = {
    'duncan': [
        (1,'PatrickF',139.83,127.38),(2,'Larson',124.20,138.00),(3,'Antony',106.85,109.44),
        (4,'Daniel',156.85,127.59),(5,'David',120.53,116.72),(6,'Kyle2',137.46,112.92),
        (7,'Raj',96.22,126.80),(8,'RyanC',137.03,121.15),(9,'Kyle',121.25,140.89),
        (10,'PatrickF',133.95,95.86),(11,'Larson',104.02,133.67),(12,'Antony',144.30,60.99),
        (13,'Daniel',124.36,118.75),(14,'David',137.61,136.35),
    ],
    'PatrickF': [
        (1,'duncan',127.38,139.83),(2,'Kyle',125.31,138.43),(3,'Larson',129.92,146.48),
        (4,'Antony',123.81,146.86),(5,'Daniel',127.93,101.28),(6,'David',83.66,80.36),
        (7,'Kyle2',105.51,135.72),(8,'Raj',103.83,145.32),(9,'RyanC',123.30,138.35),
        (10,'duncan',95.86,133.95),(11,'Kyle',97.08,105.99),(12,'Larson',72.97,125.94),
        (13,'Antony',116.09,123.24),(14,'Daniel',126.41,86.83),
    ],
    'Larson': [
        (1,'RyanC',152.21,130.31),(2,'duncan',138.00,124.20),(3,'PatrickF',146.48,129.92),
        (4,'Kyle',101.43,105.12),(5,'Antony',106.37,100.54),(6,'Daniel',125.80,82.88),
        (7,'David',119.25,108.62),(8,'Kyle2',144.87,91.59),(9,'Raj',98.71,162.63),
        (10,'RyanC',122.57,122.97),(11,'duncan',133.67,104.02),(12,'PatrickF',125.94,72.97),
        (13,'Kyle',159.29,142.66),(14,'Antony',92.33,94.66),
    ],
    'Antony': [
        (1,'Raj',118.95,107.81),(2,'RyanC',137.10,129.51),(3,'duncan',109.44,106.85),
        (4,'PatrickF',146.86,123.81),(5,'Larson',100.54,106.37),(6,'Kyle',113.22,142.67),
        (7,'Daniel',80.64,117.95),(8,'David',94.89,103.50),(9,'Kyle2',106.64,80.03),
        (10,'Raj',110.42,135.26),(11,'RyanC',105.83,101.60),(12,'duncan',60.99,144.30),
        (13,'PatrickF',123.24,116.09),(14,'Larson',94.66,92.33),
    ],
    'Daniel': [
        (1,'Kyle2',105.86,134.96),(2,'Raj',99.03,157.95),(3,'RyanC',99.01,95.75),
        (4,'duncan',127.59,156.85),(5,'PatrickF',101.28,127.93),(6,'Larson',82.88,125.80),
        (7,'Antony',117.95,80.64),(8,'Kyle',87.28,129.18),(9,'David',94.48,137.28),
        (10,'Kyle2',106.70,81.36),(11,'Raj',105.50,144.97),(12,'RyanC',122.96,93.06),
        (13,'duncan',118.75,124.36),(14,'PatrickF',126.41,86.83),
    ],
    'David': [
        (1,'Kyle',129.02,127.83),(2,'Kyle2',99.74,98.73),(3,'Raj',97.64,152.17),
        (4,'RyanC',143.44,157.82),(5,'duncan',116.72,120.53),(6,'PatrickF',80.36,83.66),
        (7,'Larson',108.62,119.25),(8,'Antony',103.50,94.89),(9,'Daniel',137.28,94.48),
        (10,'Kyle',101.04,71.80),(11,'Kyle2',129.90,80.84),(12,'Raj',75.43,114.38),
        (13,'RyanC',138.37,102.11),(14,'duncan',136.35,137.61),
    ],
    'Kyle2': [
        (1,'Daniel',134.96,105.86),(2,'David',98.73,99.74),(3,'Kyle',67.37,113.36),
        (4,'Raj',110.42,112.58),(5,'RyanC',84.63,137.15),(6,'duncan',112.92,137.46),
        (7,'PatrickF',135.72,105.51),(8,'Larson',91.59,144.87),(9,'Antony',80.03,106.64),
        (10,'Daniel',81.36,106.70),(11,'David',80.84,129.90),(12,'Kyle',85.23,129.56),
        (13,'Raj',80.03,149.22),(14,'RyanC',110.24,138.58),
    ],
    'Raj': [
        (1,'Antony',107.81,118.95),(2,'Daniel',157.95,99.03),(3,'David',152.17,97.64),
        (4,'Kyle2',112.58,110.42),(5,'Kyle',106.05,112.90),(6,'RyanC',94.55,104.21),
        (7,'duncan',126.80,96.22),(8,'PatrickF',145.32,103.83),(9,'Larson',162.63,98.71),
        (10,'Antony',135.26,110.42),(11,'Daniel',144.97,105.50),(12,'David',114.38,75.43),
        (13,'Kyle2',149.22,80.03),(14,'Kyle',151.25,135.49),
    ],
    'RyanC': [
        (1,'Larson',130.31,152.21),(2,'Antony',129.51,137.10),(3,'Daniel',95.75,99.01),
        (4,'David',157.82,143.44),(5,'Kyle2',137.15,84.63),(6,'Raj',104.21,94.55),
        (7,'Kyle',65.69,94.39),(8,'duncan',121.15,137.03),(9,'PatrickF',138.35,123.30),
        (10,'Larson',122.97,122.57),(11,'Antony',101.60,105.83),(12,'Daniel',93.06,122.96),
        (13,'David',102.11,138.37),(14,'Kyle2',138.58,110.24),
    ],
    'Kyle': [
        (1,'David',127.83,129.02),(2,'PatrickF',138.43,125.31),(3,'Kyle2',113.36,67.37),
        (4,'Larson',105.12,101.43),(5,'Raj',112.90,106.05),(6,'Antony',142.67,113.22),
        (7,'RyanC',94.39,65.69),(8,'Daniel',129.18,87.28),(9,'duncan',140.89,121.25),
        (10,'David',71.80,101.04),(11,'PatrickF',105.99,97.08),(12,'Kyle2',129.56,85.23),
        (13,'Larson',142.66,159.29),(14,'Raj',135.49,151.25),
    ],
}

# Wk15: Champ SF: duncan(2nd) beats Raj(3rd) 166.85-86.13; Larson(1st) beats Kyle(4th) 144.05-143.55
#        Consol R1: Antony(6th) beats Daniel(7th) 98.70-69.90; RyanC(5th) beats David(8th) 133.86-90.63
# Wk16: Champ Final: Larson beats duncan 153.18-115.99 → LARSON CHAMPION!
#        3rd: Raj beats Kyle 126.78-86.11
#        5th: RyanC beats Antony 97.73-96.17
#        7th: Daniel beats David 107.64-88.82
PLAYOFFS_2013 = [
    (15,'duncan','Raj',166.85,86.13,True),
    (15,'Larson','Kyle',144.05,143.55,True),
    (15,'Antony','Daniel',98.70,69.90,True),
    (15,'RyanC','David',133.86,90.63,True),
    (16,'Larson','duncan',153.18,115.99,True),
    (16,'Raj','Kyle',126.78,86.11,True),
    (16,'RyanC','Antony',97.73,96.17,True),
    (16,'Daniel','David',107.64,88.82,True),
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
for mgr, schedule in SCHED_2013.items():
    for (wk, opp, my_s, opp_s) in schedule:
        key = tuple(sorted([mgr, opp])) + (wk,)
        if key in seen: continue
        seen.add(key)
        outer,inner = (mgr,opp) if mgr<opp else (opp,mgr)
        if mgr<opp: games[(outer,inner)].append((my_s,opp_s,False))
        else:       games[(outer,inner)].append((opp_s,my_s,False))

for (wk,m1,m2,s1,s2,is_po) in PLAYOFFS_2013:
    key = tuple(sorted([m1,m2])) + (wk,)
    if key in seen: continue
    seen.add(key)
    outer,inner = (m1,m2) if m1<m2 else (m2,m1)
    if m1<m2: games[(outer,inner)].append((s1,s2,is_po))
    else:     games[(outer,inner)].append((s2,s1,is_po))

print(f"2013 games: {sum(len(v) for v in games.values())} (expect 70+8=78)")

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
            entry['last'] = {'winner':w,'score1':s_outer,'score2':s_inner,'season':'13'}

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
    'Data from 2014–2025 seasons · Historical seasons (2009–2013) compiling',
    'Data from 2013–2025 seasons · Historical seasons (2009–2012) compiling'
)
with open('kdp_report.html','w') as f: f.write(html_new)

total_p = sum(len(v) for v in existing.values())
total_g = sum(e['w1']+e['w2'] for d in existing.values() for e in d.values())
print(f"Done: {total_p} pairs, {total_g} total games")
for a,b in [('Larson','duncan'),('Raj','RyanC'),('Antony','Kyle')]:
    outer,inner=(a,b) if a<b else (b,a)
    e=existing.get(outer,{}).get(inner,{})
    print(f"  {outer} vs {inner}: w1={e.get('w1')},w2={e.get('w2')},seasons={e.get('seasons')},po={e.get('playoffs')}")
