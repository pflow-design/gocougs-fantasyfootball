import re
from collections import defaultdict

# 2012 mapping:
# 1=duncan, 2=Kyle, 3=David, 4=Raj, 5=Daniel, 6=Kyle2(DEBUT), 7=PatrickF, 8=Larson, 9=Antony, 10=RyanC
# Seeds: duncan(1st,8-6), Kyle(2nd,8-6), RyanC(3rd,10-4), PatrickF(4th,10-4)
#        Larson(5th,7-7), David(6th,6-8), Antony(7th,7-7), Raj(8th,7-7)
# No playoffs: Daniel(4-10), Kyle2(3-11)
# Final: 1=duncan(CHAMPION!), 2=Kyle, 3=RyanC, 4=PatrickF, 5=Larson, 6=David, 7=Antony, 8=Raj

SCHED_2012 = {
    'duncan': [
        (1,'Kyle',122.70,132.13),(2,'David',108.50,90.76),(3,'Raj',102.84,101.35),
        (4,'Daniel',173.21,101.50),(5,'Kyle2',128.46,88.58),(6,'PatrickF',76.54,103.25),
        (7,'Larson',138.12,75.52),(8,'Antony',118.37,108.25),(9,'RyanC',131.96,146.64),
        (10,'Kyle',111.48,143.14),(11,'David',123.66,91.54),(12,'Raj',94.99,125.27),
        (13,'Daniel',100.60,138.35),(14,'Kyle2',159.26,115.89),
    ],
    'Kyle': [
        (1,'duncan',132.13,122.70),(2,'RyanC',151.23,95.03),(3,'David',165.90,103.43),
        (4,'Raj',114.79,129.63),(5,'Daniel',135.13,79.15),(6,'Kyle2',104.84,75.05),
        (7,'PatrickF',99.15,114.77),(8,'Larson',91.88,103.28),(9,'Antony',104.01,130.58),
        (10,'duncan',143.14,111.48),(11,'RyanC',92.07,120.41),(12,'David',93.59,92.52),
        (13,'Raj',96.06,119.12),(14,'Daniel',120.15,106.17),
    ],
    'David': [
        (1,'Antony',113.75,98.81),(2,'duncan',90.76,108.50),(3,'Kyle',103.43,165.90),
        (4,'RyanC',102.65,158.96),(5,'Raj',156.29,143.08),(6,'Daniel',137.36,118.27),
        (7,'Kyle2',147.38,125.22),(8,'PatrickF',106.80,83.11),(9,'Larson',141.50,121.43),
        (10,'Antony',91.58,108.56),(11,'duncan',91.54,123.66),(12,'Kyle',92.52,93.59),
        (13,'RyanC',75.34,123.84),(14,'Raj',99.73,126.58),
    ],
    'Raj': [
        (1,'Larson',123.06,127.42),(2,'Antony',120.89,106.09),(3,'duncan',101.35,102.84),
        (4,'Kyle',129.63,114.79),(5,'David',143.08,156.29),(6,'RyanC',89.27,143.32),
        (7,'Daniel',91.62,109.59),(8,'Kyle2',105.80,74.86),(9,'PatrickF',82.40,91.28),
        (10,'Larson',89.78,128.70),(11,'Antony',120.86,120.55),(12,'duncan',125.27,94.99),
        (13,'Kyle',119.12,96.06),(14,'David',126.58,99.73),
    ],
    'Daniel': [
        (1,'PatrickF',119.20,99.49),(2,'Larson',98.17,103.50),(3,'Antony',109.37,118.92),
        (4,'duncan',101.50,173.21),(5,'Kyle',79.15,135.13),(6,'David',118.27,137.36),
        (7,'Raj',109.59,91.62),(8,'RyanC',170.26,127.16),(9,'Kyle2',96.62,103.84),
        (10,'PatrickF',98.27,128.80),(11,'Larson',135.01,136.36),(12,'Antony',110.78,111.21),
        (13,'duncan',138.35,100.60),(14,'Kyle',106.17,120.15),
    ],
    'Kyle2': [
        (1,'RyanC',121.96,138.15),(2,'PatrickF',110.69,160.87),(3,'Larson',69.33,127.14),
        (4,'Antony',136.59,92.85),(5,'duncan',88.58,128.46),(6,'Kyle',75.05,104.84),
        (7,'David',125.22,147.38),(8,'Raj',74.86,105.80),(9,'Daniel',103.84,96.62),
        (10,'RyanC',96.90,108.63),(11,'PatrickF',99.81,118.49),(12,'Larson',140.80,111.99),
        (13,'Antony',106.89,154.70),(14,'duncan',115.89,159.26),
    ],
    'PatrickF': [
        (1,'Daniel',99.49,119.20),(2,'Kyle2',160.87,110.69),(3,'RyanC',129.16,105.33),
        (4,'Larson',118.46,68.69),(5,'Antony',125.78,94.59),(6,'duncan',103.25,76.54),
        (7,'Kyle',114.77,99.15),(8,'David',83.11,106.80),(9,'Raj',91.28,82.40),
        (10,'Daniel',128.80,98.27),(11,'Kyle2',118.49,99.81),(12,'RyanC',112.53,115.56),
        (13,'Larson',101.39,112.32),(14,'Antony',142.93,68.90),
    ],
    'Larson': [
        (1,'Raj',127.42,123.06),(2,'Daniel',103.50,98.17),(3,'Kyle2',127.14,69.33),
        (4,'PatrickF',68.69,118.46),(5,'RyanC',108.51,149.31),(6,'Antony',122.88,135.14),
        (7,'duncan',75.52,138.12),(8,'Kyle',103.28,91.88),(9,'David',121.43,141.50),
        (10,'Raj',128.70,89.78),(11,'Daniel',136.36,135.01),(12,'Kyle2',111.99,140.80),
        (13,'PatrickF',112.32,101.39),(14,'RyanC',106.48,120.37),
    ],
    'Antony': [
        (1,'David',98.81,113.75),(2,'Raj',106.09,120.89),(3,'Daniel',118.92,109.37),
        (4,'Kyle2',136.59,92.85),(5,'PatrickF',94.59,125.78),(6,'Larson',135.14,122.88),
        (7,'RyanC',103.24,97.75),(8,'duncan',108.25,118.37),(9,'Kyle',130.58,104.01),
        (10,'David',108.56,91.58),(11,'Raj',120.55,120.86),(12,'Daniel',111.21,110.78),
        (13,'Kyle2',154.70,106.89),(14,'PatrickF',68.90,142.93),
    ],
    'RyanC': [
        (1,'Kyle2',138.15,121.96),(2,'Kyle',95.03,151.23),(3,'PatrickF',105.33,129.16),
        (4,'David',158.96,102.65),(5,'Larson',149.31,108.51),(6,'Raj',143.32,89.27),
        (7,'Antony',97.75,103.24),(8,'Daniel',127.16,170.26),(9,'duncan',146.64,131.96),
        (10,'Kyle2',108.63,96.90),(11,'Kyle',120.41,92.07),(12,'PatrickF',115.56,112.53),
        (13,'David',123.84,75.34),(14,'Larson',120.37,106.48),
    ],
}

# Wk15 SF: PatrickF(4th) 110.88 vs duncan(1st) 136.74 → duncan wins
#           Kyle(2nd) 122.84 vs RyanC(3rd) 94.73 → Kyle wins
#  Consol: David(6th) 140.07 vs Raj(8th) 67.57 → David wins
#           Larson(5th) 103.19 vs Antony(7th) 82.19 → Larson wins
# Wk16 Final: duncan 156.61 vs Kyle 132.79 → duncan CHAMPION!
#       3rd: RyanC 145.65 vs PatrickF 105.33 → RyanC wins
#       5th: Larson 132.91 vs David 127.48 → Larson wins
#       7th: Antony 104.02 vs Raj 97.62 → Antony wins
PLAYOFFS_2012 = [
    (15,'PatrickF','duncan',110.88,136.74,True),
    (15,'Kyle','RyanC',122.84,94.73,True),
    (15,'David','Raj',140.07,67.57,True),
    (15,'Larson','Antony',103.19,82.19,True),
    (16,'duncan','Kyle',156.61,132.79,True),
    (16,'RyanC','PatrickF',145.65,105.33,True),
    (16,'Larson','David',132.91,127.48,True),
    (16,'Antony','Raj',104.02,97.62,True),
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
for mgr, schedule in SCHED_2012.items():
    for (wk, opp, my_s, opp_s) in schedule:
        key = tuple(sorted([mgr, opp])) + (wk,)
        if key in seen: continue
        seen.add(key)
        outer,inner = (mgr,opp) if mgr<opp else (opp,mgr)
        if mgr<opp: games[(outer,inner)].append((my_s,opp_s,False))
        else:       games[(outer,inner)].append((opp_s,my_s,False))

for (wk,m1,m2,s1,s2,is_po) in PLAYOFFS_2012:
    key = tuple(sorted([m1,m2])) + (wk,)
    if key in seen: continue
    seen.add(key)
    outer,inner = (m1,m2) if m1<m2 else (m2,m1)
    if m1<m2: games[(outer,inner)].append((s1,s2,is_po))
    else:     games[(outer,inner)].append((s2,s1,is_po))

print(f"2012 games: {sum(len(v) for v in games.values())} (expect 70+8=78)")

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
            entry['last'] = {'winner':w,'score1':s_outer,'score2':s_inner,'season':'12'}

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
    'Data from 2013–2025 seasons · Historical seasons (2009–2012) compiling',
    'Data from 2012–2025 seasons · Historical seasons (2009–2011) compiling'
)
with open('kdp_report.html','w') as f: f.write(html_new)

total_p = sum(len(v) for v in existing.values())
total_g = sum(e['w1']+e['w2'] for d in existing.values() for e in d.values())
print(f"Done: {total_p} pairs, {total_g} total games")
# Spot checks
for a,b in [('duncan','Kyle'),('Larson','RyanC'),('Antony','Kyle2')]:
    outer,inner=(a,b) if a<b else (b,a)
    e=existing.get(outer,{}).get(inner,{})
    print(f"  {outer} vs {inner}: w1={e.get('w1')},w2={e.get('w2')},seasons={e.get('seasons')},po={e.get('playoffs')}")
