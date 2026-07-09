import re
from collections import defaultdict

# 2018 mapping:
# 1:RogersGoodell→duncan, 2:WokeUpFeelinDangerus→David, 3:TonyThePony→Antony
# 4:Larson→Larson(hidden), 5:MyBallZachErtz→Daniel, 6:RussellSprouts→RyanC
# 7:SwingYourSword→Kyle, 8:Dicksons3rdLeg→PatrickF, 9:DoubleDeuce→Kyle2, 10:ShmeyMaker→Raj

SCHED_2018 = {
    'duncan': [
        (1,'David',106.17,148.26),(2,'Antony',136.75,109.13),(3,'Larson',110.96,120.50),
        (4,'Daniel',158.98,149.36),(5,'RyanC',97.82,105.37),(6,'Kyle',105.16,106.92),
        (7,'PatrickF',124.85,85.55),(8,'Kyle2',117.04,135.35),(9,'Raj',88.36,136.46),
        (10,'David',86.82,140.63),(11,'Antony',156.25,134.74),(12,'Larson',102.49,130.85),
        (13,'Daniel',85.51,137.85),(14,'RyanC',80.74,156.72),
    ],
    'David': [
        (1,'duncan',148.26,106.17),(2,'Raj',112.47,146.31),(3,'Antony',98.50,129.80),
        (4,'Larson',97.90,115.53),(5,'Daniel',95.64,167.00),(6,'RyanC',106.59,158.70),
        (7,'Kyle',107.81,131.56),(8,'PatrickF',112.05,92.20),(9,'Kyle2',116.51,144.09),
        (10,'duncan',140.63,86.82),(11,'Raj',81.50,149.08),(12,'Antony',113.88,138.68),
        (13,'Larson',63.78,126.08),(14,'Daniel',91.68,116.08),
    ],
    'Antony': [
        (1,'Kyle2',134.91,175.89),(2,'duncan',109.13,136.75),(3,'David',129.80,98.50),
        (4,'Raj',129.15,135.66),(5,'Larson',135.94,137.28),(6,'Daniel',119.16,150.43),
        (7,'RyanC',140.53,136.19),(8,'Kyle',127.88,133.37),(9,'PatrickF',115.56,145.32),
        (10,'Kyle2',107.73,134.36),(11,'duncan',134.74,156.25),(12,'David',138.68,113.88),
        (13,'Raj',105.12,149.20),(14,'Larson',147.20,123.80),
    ],
    'Larson': [
        (1,'PatrickF',111.16,165.63),(2,'Kyle2',110.40,140.48),(3,'duncan',120.50,110.96),
        (4,'David',115.53,97.90),(5,'Antony',137.28,135.94),(6,'Raj',90.09,162.84),
        (7,'Daniel',137.87,97.39),(8,'RyanC',159.49,147.98),(9,'Kyle',80.95,125.97),
        (10,'PatrickF',128.48,166.54),(11,'Kyle2',121.31,120.64),(12,'duncan',130.85,102.49),
        (13,'David',126.08,63.78),(14,'Antony',123.80,147.20),
    ],
    'Daniel': [
        (1,'Kyle',116.85,108.53),(2,'PatrickF',121.66,125.26),(3,'Kyle2',94.59,116.79),
        (4,'duncan',149.36,158.98),(5,'David',167.00,95.64),(6,'Antony',150.43,119.16),
        (7,'Larson',97.39,137.87),(8,'Raj',120.14,166.39),(9,'RyanC',108.12,126.70),
        (10,'Kyle',123.52,99.62),(11,'PatrickF',91.57,168.42),(12,'Kyle2',113.36,161.01),
        (13,'duncan',137.85,85.51),(14,'David',116.08,91.68),
    ],
    'RyanC': [
        (1,'Raj',90.05,92.14),(2,'Kyle',134.41,115.60),(3,'PatrickF',99.02,129.28),
        (4,'Kyle2',139.29,162.50),(5,'duncan',105.37,97.82),(6,'David',158.70,106.59),
        (7,'Antony',136.19,140.53),(8,'Larson',147.98,159.49),(9,'Daniel',126.70,108.12),
        (10,'Raj',157.35,115.89),(11,'Kyle',104.67,55.52),(12,'PatrickF',157.22,99.87),
        (13,'Kyle2',150.08,162.07),(14,'duncan',156.72,80.74),
    ],
    'Kyle': [
        (1,'Daniel',108.53,116.85),(2,'RyanC',115.60,134.41),(3,'Raj',97.40,102.00),
        (4,'PatrickF',103.36,137.91),(5,'Kyle2',129.47,127.40),(6,'duncan',106.92,105.16),
        (7,'David',131.56,107.81),(8,'Antony',133.37,127.88),(9,'Larson',125.97,80.95),
        (10,'Daniel',99.62,123.52),(11,'RyanC',55.52,104.67),(12,'Raj',88.44,162.62),
        (13,'PatrickF',85.33,59.28),(14,'Kyle2',97.71,140.04),
    ],
    'PatrickF': [
        (1,'Larson',165.63,111.16),(2,'Daniel',125.26,121.66),(3,'RyanC',129.28,99.02),
        (4,'Kyle',137.91,103.36),(5,'Raj',101.52,107.69),(6,'Kyle2',145.03,109.38),
        (7,'duncan',85.55,124.85),(8,'David',92.20,112.05),(9,'Antony',145.32,115.56),
        (10,'Larson',166.54,128.48),(11,'Daniel',168.42,91.57),(12,'RyanC',99.87,157.22),
        (13,'Kyle',59.28,85.33),(14,'Raj',113.01,106.42),
    ],
    'Kyle2': [
        (1,'Antony',175.89,134.91),(2,'Larson',140.48,110.40),(3,'Daniel',116.79,94.59),
        (4,'RyanC',162.50,139.29),(5,'Kyle',127.40,129.47),(6,'PatrickF',109.38,145.03),
        (7,'Raj',125.78,171.76),(8,'duncan',135.35,117.04),(9,'David',144.09,116.51),
        (10,'Antony',134.36,107.73),(11,'Larson',120.64,121.31),(12,'Daniel',161.01,113.36),
        (13,'RyanC',162.07,150.08),(14,'Kyle',140.04,97.71),
    ],
    'Raj': [
        (1,'RyanC',92.14,90.05),(2,'David',146.31,112.47),(3,'Kyle',102.00,97.40),
        (4,'Antony',135.66,129.15),(5,'PatrickF',107.69,101.52),(6,'Larson',162.84,90.09),
        (7,'Kyle2',171.76,125.78),(8,'Daniel',166.39,120.14),(9,'duncan',136.46,88.36),
        (10,'RyanC',115.89,157.35),(11,'David',149.08,81.50),(12,'Kyle',162.62,88.44),
        (13,'Antony',149.20,105.12),(14,'PatrickF',106.42,113.01),
    ],
}

# Playoffs 2018: seeds = Raj(12-2,s1), Kyle2(10-4,s2), PatrickF(9-5,s3), RyanC(8-6,s4)
# Consolation: seeds 5-8 = Daniel(6-8,5th), Larson(8-6,6th), Antony(4-10,7th), Kyle(6-8,8th)
# Duncan(4-10,9th) and David(3-11,10th) had no consolation games
PLAYOFFS_2018 = [
    # Championship bracket
    (15,'Kyle2','PatrickF',99.79,84.18,True),    # SF, Kyle2 wins
    (15,'RyanC','Raj',116.72,92.32,True),         # SF, RyanC wins (upset!)
    (16,'RyanC','Kyle2',157.43,93.61,True),       # Final, RyanC champion!
    (16,'PatrickF','Raj',106.54,105.62,True),     # 3rd place, PatrickF wins
    # Consolation bracket
    (15,'Larson','Antony',96.35,78.44,True),      # Consolation R1, Larson wins
    (15,'Daniel','Kyle',119.23,58.00,True),       # Consolation R1, Daniel wins
    (16,'Antony','Kyle',143.63,93.81,True),       # 7th/8th, Antony wins
    (16,'Daniel','Larson',145.24,127.48,True),    # 5th/6th, Daniel wins
]

# ── Parse existing h2hData from kdp_report.html ───────────────────────────────
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
for mgr, schedule in SCHED_2018.items():
    for (wk, opp, my_s, opp_s) in schedule:
        key = tuple(sorted([mgr, opp])) + (wk,)
        if key in seen: continue
        seen.add(key)
        outer,inner = (mgr,opp) if mgr<opp else (opp,mgr)
        if mgr<opp: games[(outer,inner)].append((my_s,opp_s,False))
        else:       games[(outer,inner)].append((opp_s,my_s,False))

for (wk,m1,m2,s1,s2,is_po) in PLAYOFFS_2018:
    key = tuple(sorted([m1,m2])) + (wk,)
    if key in seen: continue
    seen.add(key)
    outer,inner = (m1,m2) if m1<m2 else (m2,m1)
    if m1<m2: games[(outer,inner)].append((s1,s2,is_po))
    else:     games[(outer,inner)].append((s2,s1,is_po))

print(f"2018 games: {sum(len(v) for v in games.values())} (expect 45+8=53)")

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
            entry['last'] = {'winner':w,'score1':s_outer,'score2':s_inner,'season':'18'}

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
h2h_start = html.find('var h2hData = {')
h2h_end   = html.find('\n};', h2h_start) + 3
html_new = html[:h2h_start] + out + html[h2h_end:]
html_new = html_new.replace(
    'Data from 2019–2025 seasons · Historical seasons (2009–2018) compiling',
    'Data from 2018–2025 seasons · Historical seasons (2009–2017) compiling'
)
with open('kdp_report.html','w') as f: f.write(html_new)

total_p = sum(len(v) for v in existing.values())
total_g = sum(e['w1']+e['w2'] for d in existing.values() for e in d.values())
print(f"Done: {total_p} pairs, {total_g} total games")
# Spot checks
for a,b in [('Larson','Raj'),('Antony','Larson'),('Kyle2','Larson')]:
    outer,inner = (a,b) if a<b else (b,a)
    e = existing.get(outer,{}).get(inner,{})
    print(f"  {outer} vs {inner}: w1={e.get('w1')},w2={e.get('w2')},seasons={e.get('seasons')},po={e.get('playoffs')}")
