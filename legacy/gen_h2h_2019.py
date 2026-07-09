import re
from collections import defaultdict

# 2019 mapping:
# 1:Candyman→duncan, 2:WokeUpFeelinDangerus→David, 3:MixonItUp→Ryan
# 4:Larson→Antony(hidden), 5:MyBallZachErtz→Daniel, 6:RussellSprouts→RyanC
# 7:SwingYourSword→Kyle, 8:DicksonYourFace→PatrickF, 9:DoubleDeuce→Kyle2, 10:ShmeyMaker→Raj

SCHED_2019 = {
    'duncan': [
        (1,'David',97.56,151.23),(2,'Ryan',125.44,98.37),(3,'Antony',108.04,118.10),
        (4,'Daniel',124.94,76.07),(5,'RyanC',146.38,141.55),(6,'Kyle',101.14,116.05),
        (7,'PatrickF',94.74,107.23),(8,'Kyle2',125.45,125.05),(9,'Raj',116.25,101.40),
        (10,'David',137.62,133.13),(11,'Ryan',151.85,99.54),(12,'Antony',160.86,86.22),
        (13,'Daniel',99.59,123.86),(14,'RyanC',125.54,102.51),
    ],
    'David': [
        (1,'duncan',151.23,97.56),(2,'Raj',124.88,98.86),(3,'Ryan',139.12,130.99),
        (4,'Antony',136.46,110.68),(5,'Daniel',99.85,114.05),(6,'RyanC',119.17,109.70),
        (7,'Kyle',125.38,113.64),(8,'PatrickF',96.96,117.17),(9,'Kyle2',124.34,69.19),
        (10,'duncan',133.13,137.62),(11,'Raj',148.16,100.16),(12,'Ryan',106.46,94.63),
        (13,'Antony',125.54,121.16),(14,'Daniel',141.98,108.59),
    ],
    'Ryan': [
        (1,'Kyle2',116.04,109.15),(2,'duncan',98.37,125.44),(3,'David',130.99,139.12),
        (4,'Raj',88.41,101.76),(5,'Antony',177.82,119.07),(6,'Daniel',117.36,135.43),
        (7,'RyanC',49.06,126.86),(8,'Kyle',103.78,149.98),(9,'PatrickF',137.62,98.83),
        (10,'Kyle2',128.07,77.50),(11,'duncan',99.54,151.85),(12,'David',94.63,106.46),
        (13,'Raj',84.29,95.89),(14,'Antony',98.77,79.10),
    ],
    'Antony': [
        (1,'PatrickF',94.19,146.91),(2,'Kyle2',116.54,91.82),(3,'duncan',118.10,108.04),
        (4,'David',110.68,136.46),(5,'Ryan',119.07,177.82),(6,'Raj',116.20,121.31),
        (7,'Daniel',77.13,70.56),(8,'RyanC',104.14,125.74),(9,'Kyle',116.04,149.04),
        (10,'PatrickF',119.00,100.84),(11,'Kyle2',107.60,121.65),(12,'duncan',86.22,160.86),
        (13,'David',121.16,125.54),(14,'Ryan',79.10,98.77),
    ],
    'Daniel': [
        (1,'Kyle',97.97,110.72),(2,'PatrickF',94.67,83.26),(3,'Kyle2',145.47,144.22),
        (4,'duncan',76.07,124.94),(5,'David',114.05,99.85),(6,'Ryan',135.43,117.36),
        (7,'Antony',70.56,77.13),(8,'Raj',113.11,157.83),(9,'RyanC',169.35,109.01),
        (10,'Kyle',153.01,102.46),(11,'PatrickF',109.42,76.16),(12,'Kyle2',92.31,95.70),
        (13,'duncan',123.86,99.59),(14,'David',108.59,141.98),
    ],
    'RyanC': [
        (1,'Raj',99.06,132.36),(2,'Kyle',106.28,164.79),(3,'PatrickF',139.06,81.26),
        (4,'Kyle2',112.19,114.88),(5,'duncan',141.55,146.38),(6,'David',109.70,119.17),
        (7,'Ryan',126.86,49.06),(8,'Antony',125.74,104.14),(9,'Daniel',109.01,169.35),
        (10,'Raj',66.02,154.45),(11,'Kyle',119.49,82.61),(12,'PatrickF',133.60,95.57),
        (13,'Kyle2',111.59,102.90),(14,'duncan',102.51,125.54),
    ],
    'Kyle': [
        (1,'Daniel',110.72,97.97),(2,'RyanC',164.79,106.28),(3,'Raj',103.50,127.84),
        (4,'PatrickF',107.80,98.34),(5,'Kyle2',117.64,152.87),(6,'duncan',116.05,101.14),
        (7,'David',113.64,125.38),(8,'Ryan',149.98,103.78),(9,'Antony',149.04,116.04),
        (10,'Daniel',102.46,153.01),(11,'RyanC',119.49,82.61),(12,'Raj',117.98,160.89),
        (13,'PatrickF',100.70,127.42),(14,'Kyle2',120.83,90.06),
    ],
    'PatrickF': [
        (1,'Antony',146.91,94.19),(2,'Daniel',83.26,94.67),(3,'RyanC',81.26,139.06),
        (4,'Kyle',98.34,107.80),(5,'Raj',110.44,132.74),(6,'Kyle2',118.85,67.38),
        (7,'duncan',107.23,94.74),(8,'David',117.17,96.96),(9,'Ryan',98.83,137.62),
        (10,'Antony',100.84,119.00),(11,'Daniel',76.16,109.42),(12,'RyanC',95.57,133.60),
        (13,'Kyle',127.42,100.70),(14,'Raj',136.76,129.35),
    ],
    'Kyle2': [
        (1,'Ryan',109.15,116.04),(2,'Antony',91.82,116.54),(3,'Daniel',144.22,145.47),
        (4,'RyanC',114.88,112.19),(5,'Kyle',152.87,117.64),(6,'PatrickF',67.38,118.85),
        (7,'Raj',110.84,152.32),(8,'duncan',125.05,125.45),(9,'David',69.19,124.34),
        (10,'Ryan',77.50,128.07),(11,'Antony',121.65,107.60),(12,'Daniel',95.70,92.31),
        (13,'RyanC',102.90,111.59),(14,'Kyle',90.06,120.83),
    ],
    'Raj': [
        (1,'RyanC',132.36,99.06),(2,'David',98.86,124.88),(3,'Kyle',127.84,103.50),
        (4,'Ryan',101.76,88.41),(5,'PatrickF',132.74,110.44),(6,'Antony',121.31,116.20),
        (7,'Kyle2',152.32,110.84),(8,'Daniel',157.83,113.11),(9,'duncan',101.40,116.25),
        (10,'RyanC',154.45,66.02),(11,'David',100.16,148.16),(12,'Kyle',160.89,117.98),
        (13,'Ryan',95.89,84.29),(14,'PatrickF',129.35,136.76),
    ],
}

# Playoffs 2019 (wk15=SF, wk16=Final/3rd/consolation)
# Seeds: 1=David, 2=Raj, 3=duncan, 4=Daniel
# Consolation (wk16 only): 5th/6th Kyle vs PatrickF, 7th/8th Ryan vs RyanC
# Antony and Kyle2 had no playoff games
PLAYOFFS_2019 = [
    (15,'David','Daniel',151.77,91.28,True),    # SF1, David wins
    (15,'Raj','duncan',134.51,163.82,True),     # SF2, duncan wins (upset!)
    (16,'David','duncan',103.21,164.05,True),   # Final, duncan champion!
    (16,'Raj','Daniel',101.40,105.00,True),     # 3rd place, Daniel wins
    (16,'Kyle','PatrickF',136.34,99.05,True),   # 5th/6th, Kyle wins
    (16,'Ryan','RyanC',103.69,102.74,True),     # 7th/8th, Ryan wins (0.95!)
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

def get_or_create(a,b):
    outer,inner=(a,b) if a<b else (b,a)
    if outer not in existing: existing[outer]={}
    if inner not in existing[outer]:
        existing[outer][inner]={'w1':0,'w2':0,'pf1':0.0,'pf2':0.0,
                                'big1':None,'big2':None,'last':None,'playoffs':0,'seasons':0}
    return outer,inner,existing[outer][inner]

games=defaultdict(list); seen=set()
for mgr,schedule in SCHED_2019.items():
    for (wk,opp,my_s,opp_s) in schedule:
        key=tuple(sorted([mgr,opp]))+(wk,)
        if key in seen: continue
        seen.add(key)
        outer,inner=(mgr,opp) if mgr<opp else (opp,mgr)
        if mgr<opp: games[(outer,inner)].append((my_s,opp_s,False))
        else:       games[(outer,inner)].append((opp_s,my_s,False))

for (wk,m1,m2,s1,s2,is_po) in PLAYOFFS_2019:
    outer,inner=(m1,m2) if m1<m2 else (m2,m1)
    if m1<m2: games[(outer,inner)].append((s1,s2,is_po))
    else:     games[(outer,inner)].append((s2,s1,is_po))

print(f"2019 games: {sum(len(v) for v in games.values())} (expect 70+6=76)")

seasons_added=set()
for (outer,inner),game_list in games.items():
    _,_,entry=get_or_create(outer,inner)
    if (outer,inner) not in seasons_added:
        entry['seasons']+=1; seasons_added.add((outer,inner))
    for (s_outer,s_inner,is_po) in game_list:
        if s_outer>s_inner: entry['w1']+=1
        else:               entry['w2']+=1
        entry['pf1']=round(entry['pf1']+s_outer,2)
        entry['pf2']=round(entry['pf2']+s_inner,2)
        if entry['big1'] is None or s_outer>entry['big1']: entry['big1']=s_outer
        if entry['big2'] is None or s_inner>entry['big2']: entry['big2']=s_inner
        if is_po: entry['playoffs']+=1
        if entry['last'] is None:
            w=outer if s_outer>s_inner else inner
            entry['last']={'winner':w,'score1':s_outer,'score2':s_inner,'season':'19'}

lines=['var h2hData = {']
for i,outer in enumerate(sorted(existing.keys())):
    lines.append(f"  '{outer}': {{")
    inner_items=list(existing[outer].items())
    for j,(inner,e) in enumerate(inner_items):
        last=e['last']
        ls=(f"{{winner:'{last['winner']}',score1:{last['score1']:.2f},"
            f"score2:{last['score2']:.2f},season:'{last['season']}'}}")
        b1=f"{e['big1']:.2f}" if e['big1'] is not None else 'null'
        b2=f"{e['big2']:.2f}" if e['big2'] is not None else 'null'
        c='' if j==len(inner_items)-1 else ','
        lines.append(f"    '{inner}': {{w1:{e['w1']},w2:{e['w2']},"
                     f"pf1:{e['pf1']:.2f},pf2:{e['pf2']:.2f},"
                     f"big1:{b1},big2:{b2},last:{ls},"
                     f"playoffs:{e['playoffs']},seasons:{e['seasons']}}}{c}")
    c='' if i==len(existing)-1 else ','
    lines.append(f"  }}{c}")
lines.append('};')
out='\n'.join(lines)
with open('h2h_all.js','w') as f: f.write(out)

with open('kdp_report.html') as f: html=f.read()
h2h_start=html.find('var h2hData = {'); h2h_end=html.find('\n};',h2h_start)+3
html_new=html[:h2h_start]+out+html[h2h_end:]
html_new=html_new.replace(
    'Data from 2020–2025 seasons · Historical seasons (2009–2019) compiling',
    'Data from 2019–2025 seasons · Historical seasons (2009–2018) compiling'
)
with open('kdp_report.html','w') as f: f.write(html_new)

total_p=sum(len(v) for v in existing.values())
total_g=sum(e['w1']+e['w2'] for d in existing.values() for e in d.values())
print(f"Done: {total_p} pairs, {total_g} total games")
# Spot checks
for a,b in [('Antony','duncan'),('Antony','Kyle'),('Ryan','RyanC')]:
    outer,inner=(a,b) if a<b else (b,a)
    e=existing.get(outer,{}).get(inner,{})
    print(f"  {outer} vs {inner}: w1={e.get('w1')},w2={e.get('w2')},seasons={e.get('seasons')},po={e.get('playoffs')}")
