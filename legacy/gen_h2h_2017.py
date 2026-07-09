import re
from collections import defaultdict

# 2017 mapping:
# 1:RogersGoodell→duncan, 2:MariortaKart→David, 3:Falk4Heisman→Antony
# 4:Larson→Larson, 5:MyBallZachErtz→Daniel, 6:RussellSprouts→RyanC
# 7:SwingYourSword→Kyle, 8:LACYsCHINESEFOOD→PatrickF, 9:BradyAndTheSkins→Kyle2, 10:ShmeyMaker→Raj

SCHED_2017 = {
    'duncan': [
        (1,'David',113.38,129.04),(2,'Antony',93.09,128.21),(3,'Larson',90.78,150.43),
        (4,'Daniel',82.59,124.93),(5,'RyanC',106.17,100.08),(6,'Kyle',101.01,99.86),
        (7,'PatrickF',105.87,86.24),(8,'Kyle2',96.07,92.87),(9,'Raj',135.51,107.87),
        (10,'David',101.46,119.37),(11,'Antony',142.03,116.15),(12,'Larson',133.44,124.06),
        (13,'Daniel',129.40,120.98),(14,'RyanC',109.83,106.54),
    ],
    'David': [
        (1,'duncan',129.04,113.38),(2,'Raj',107.34,144.50),(3,'Antony',100.47,108.49),
        (4,'Larson',89.61,113.87),(5,'Daniel',105.36,133.88),(6,'RyanC',118.13,117.93),
        (7,'Kyle',88.02,135.30),(8,'PatrickF',96.39,101.77),(9,'Kyle2',71.80,148.37),
        (10,'duncan',119.37,101.46),(11,'Raj',86.64,119.84),(12,'Antony',92.43,111.61),
        (13,'Larson',128.03,109.34),(14,'Daniel',113.45,151.37),
    ],
    'Antony': [
        (1,'Kyle2',107.46,85.25),(2,'duncan',128.21,93.09),(3,'David',108.49,100.47),
        (4,'Raj',79.11,137.18),(5,'Larson',126.65,111.03),(6,'Daniel',112.89,100.23),
        (7,'RyanC',113.84,130.22),(8,'Kyle',95.69,92.56),(9,'PatrickF',82.77,105.78),
        (10,'Kyle2',84.84,154.53),(11,'duncan',116.15,142.03),(12,'David',111.61,92.43),
        (13,'Raj',101.79,130.84),(14,'Larson',96.41,141.71),
    ],
    'Larson': [
        (1,'PatrickF',82.91,108.54),(2,'Kyle2',100.20,116.78),(3,'duncan',150.43,90.78),
        (4,'David',113.87,89.61),(5,'Antony',111.03,126.65),(6,'Raj',151.62,73.70),
        (7,'Daniel',109.99,132.53),(8,'RyanC',140.75,98.26),(9,'Kyle',106.76,78.98),
        (10,'PatrickF',119.95,103.12),(11,'Kyle2',113.65,155.20),(12,'duncan',124.06,133.44),
        (13,'David',109.34,128.03),(14,'Antony',141.71,96.41),
    ],
    'Daniel': [
        (1,'Kyle',88.13,97.44),(2,'PatrickF',93.23,68.67),(3,'Kyle2',116.84,120.86),
        (4,'duncan',124.93,82.59),(5,'David',133.88,105.36),(6,'Antony',100.23,112.89),
        (7,'Larson',132.53,109.99),(8,'Raj',110.65,131.87),(9,'RyanC',95.71,99.35),
        (10,'Kyle',103.38,111.26),(11,'PatrickF',130.32,122.67),(12,'Kyle2',119.75,154.55),
        (13,'duncan',120.98,129.40),(14,'David',151.37,113.45),
    ],
    'RyanC': [
        (1,'Raj',99.90,98.41),(2,'Kyle',117.84,87.22),(3,'PatrickF',118.13,107.83),
        (4,'Kyle2',117.61,122.48),(5,'duncan',100.08,106.17),(6,'David',117.93,118.13),
        (7,'Antony',130.22,113.84),(8,'Larson',98.26,140.75),(9,'Daniel',99.35,95.71),
        (10,'Raj',109.59,151.84),(11,'Kyle',104.11,78.93),(12,'PatrickF',93.79,108.18),
        (13,'Kyle2',82.69,102.18),(14,'duncan',106.54,109.83),
    ],
    'Kyle': [
        (1,'Daniel',97.44,88.13),(2,'RyanC',87.22,117.84),(3,'Raj',91.11,102.76),
        (4,'PatrickF',59.51,111.49),(5,'Kyle2',73.34,78.13),(6,'duncan',99.86,101.01),
        (7,'David',135.30,88.02),(8,'Antony',92.56,95.69),(9,'Larson',78.98,106.76),
        (10,'Daniel',111.26,103.38),(11,'RyanC',78.93,104.11),(12,'Raj',102.26,129.85),
        (13,'PatrickF',103.01,101.05),(14,'Kyle2',77.55,108.00),
    ],
    'PatrickF': [
        (1,'Larson',108.54,82.91),(2,'Daniel',68.67,93.23),(3,'RyanC',107.83,118.13),
        (4,'Kyle',111.49,59.51),(5,'Raj',105.88,102.81),(6,'Kyle2',105.04,101.28),
        (7,'duncan',86.24,105.87),(8,'David',101.77,96.39),(9,'Antony',105.78,82.77),
        (10,'Larson',103.12,119.95),(11,'Daniel',122.67,130.32),(12,'RyanC',108.18,93.79),
        (13,'Kyle',101.05,103.01),(14,'Raj',107.24,119.82),
    ],
    'Kyle2': [
        (1,'Antony',85.25,107.46),(2,'Larson',116.78,100.20),(3,'Daniel',120.86,116.84),
        (4,'RyanC',122.48,117.61),(5,'Kyle',78.13,73.34),(6,'PatrickF',101.28,105.04),
        (7,'Raj',142.79,116.85),(8,'duncan',92.87,96.07),(9,'David',148.37,71.80),
        (10,'Antony',154.53,84.84),(11,'Larson',155.20,113.65),(12,'Daniel',154.55,119.75),
        (13,'RyanC',102.18,82.69),(14,'Kyle',108.00,77.55),
    ],
    'Raj': [
        (1,'RyanC',98.41,99.90),(2,'David',144.50,107.34),(3,'Kyle',102.76,91.11),
        (4,'Antony',137.18,79.11),(5,'PatrickF',102.81,105.88),(6,'Larson',73.70,151.62),
        (7,'Kyle2',116.85,142.79),(8,'Daniel',131.87,110.65),(9,'duncan',107.87,135.51),
        (10,'RyanC',151.84,109.59),(11,'David',119.84,86.64),(12,'Kyle',129.85,102.26),
        (13,'Antony',130.84,101.79),(14,'PatrickF',119.82,107.24),
    ],
}

# Playoffs 2017: Seeds = Kyle2(11-3,s1), Raj(9-5,s2), Larson(7-7,s3), duncan(9-5,s4)
# Consolation seeds 5-8: RyanC(6-8,5th), Daniel(6-8,6th), Antony(7-7,7th), PatrickF(7-7,8th)
# David(4-10,9th) and Kyle(4-10,10th) had no consolation games
PLAYOFFS_2017 = [
    # Championship bracket wk15
    (15,'Kyle2','Larson',121.76,98.48,True),    # SF1, Kyle2 wins
    (15,'Raj','duncan',131.13,102.87,True),     # SF2, Raj wins
    # Consolation wk15
    (15,'Daniel','PatrickF',104.04,86.43,True), # Consolation R1, Daniel wins
    (15,'RyanC','Antony',129.84,89.44,True),    # Consolation R1, RyanC wins
    # Championship bracket wk16
    (16,'Kyle2','Raj',132.36,93.12,True),       # Final, Kyle2 champion!
    (16,'Larson','duncan',104.45,79.31,True),   # 3rd place, Larson wins
    # Consolation wk16
    (16,'Antony','PatrickF',79.47,73.93,True),  # 7th/8th, Antony wins 7th
    (16,'RyanC','Daniel',126.38,106.47,True),   # 5th/6th, RyanC wins 5th
]

# ── Parse existing h2hData ────────────────────────────────────────────────────
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
for mgr, schedule in SCHED_2017.items():
    for (wk, opp, my_s, opp_s) in schedule:
        key = tuple(sorted([mgr, opp])) + (wk,)
        if key in seen: continue
        seen.add(key)
        outer,inner = (mgr,opp) if mgr<opp else (opp,mgr)
        if mgr<opp: games[(outer,inner)].append((my_s,opp_s,False))
        else:       games[(outer,inner)].append((opp_s,my_s,False))

for (wk,m1,m2,s1,s2,is_po) in PLAYOFFS_2017:
    key = tuple(sorted([m1,m2])) + (wk,)
    if key in seen: continue
    seen.add(key)
    outer,inner = (m1,m2) if m1<m2 else (m2,m1)
    if m1<m2: games[(outer,inner)].append((s1,s2,is_po))
    else:     games[(outer,inner)].append((s2,s1,is_po))

print(f"2017 games: {sum(len(v) for v in games.values())} (expect 70+8=78)")

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
            entry['last'] = {'winner':w,'score1':s_outer,'score2':s_inner,'season':'17'}

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
with open('h2h_all.js','w') as f: f.write(out)

with open('kdp_report.html') as f: html = f.read()
h2h_start = html.find('var h2hData = {'); h2h_end = html.find('\n};',h2h_start)+3
html_new = html[:h2h_start]+out+html[h2h_end:]
html_new = html_new.replace(
    'Data from 2018–2025 seasons · Historical seasons (2009–2017) compiling',
    'Data from 2017–2025 seasons · Historical seasons (2009–2016) compiling'
)
with open('kdp_report.html','w') as f: f.write(html_new)

total_p = sum(len(v) for v in existing.values())
total_g = sum(e['w1']+e['w2'] for d in existing.values() for e in d.values())
print(f"Done: {total_p} pairs, {total_g} total games")
# Spot check Larson wins 2017 3rd place (beat duncan)
for a,b in [('Larson','duncan'),('Kyle2','Larson'),('Antony','Larson')]:
    outer,inner=(a,b) if a<b else (b,a)
    e=existing.get(outer,{}).get(inner,{})
    print(f"  {outer} vs {inner}: w1={e.get('w1')},w2={e.get('w2')},seasons={e.get('seasons')},po={e.get('playoffs')}")
