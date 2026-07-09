"""
Fix: 2019 hidden team "Larson" was wrongly attributed to 'Antony'.
Antony was NOT in the league in 2019. The hidden scmid=4 team is a separate
person keyed as 'Larson'. This script removes 2019 games from Antony's pairs
and adds them under Larson.
"""
import re

# 2019 games involving the hidden team (wrongly labeled Antony, should be Larson)
# Format: (week, opp, my_score_as_outer, opp_score, outer_key)
# Note: outer_key is whichever of (Larson/Antony, opp) sorts first alphabetically
GAMES_2019_LARSON = [
    # (wk, opp, larson_score, opp_score)
    (1, 'PatrickF', 94.19, 146.91),
    (2, 'Kyle2',   116.54,  91.82),
    (3, 'duncan',  118.10, 108.04),
    (4, 'David',   110.68, 136.46),
    (5, 'Ryan',    119.07, 177.82),
    (6, 'Raj',     116.20, 121.31),
    (7, 'Daniel',   77.13,  70.56),
    (8, 'RyanC',   104.14, 125.74),
    (9, 'Kyle',    116.04, 149.04),
    (10,'PatrickF',119.00, 100.84),
    (11,'Kyle2',   107.60, 121.65),
    (12,'duncan',   86.22, 160.86),
    (13,'David',   121.16, 125.54),
    (14,'Ryan',     79.10,  98.77),
]

# ── parse current kdp_report.html ────────────────────────────────────────────
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

before_count = sum(e['w1']+e['w2'] for d in existing.values() for e in d.values())
print(f"Before: {sum(len(v) for v in existing.values())} pairs, {before_count} games")

def get_entry(a, b):
    outer,inner=(a,b) if a<b else (b,a)
    return outer,inner,existing[outer][inner]

def get_or_create(a, b):
    outer,inner=(a,b) if a<b else (b,a)
    if outer not in existing: existing[outer]={}
    if inner not in existing[outer]:
        existing[outer][inner]={'w1':0,'w2':0,'pf1':0.0,'pf2':0.0,
                                'big1':None,'big2':None,'last':None,'playoffs':0,'seasons':0}
    return outer,inner,existing[outer][inner]

# Step 1: Remove 2019 contributions from Antony pairs
antony_pairs_fixed = set()
for (wk, opp, larson_s, opp_s) in GAMES_2019_LARSON:
    # When this was Antony, it was stored with Antony as the player
    # Determine old outer/inner with Antony
    a_outer, a_inner, e = get_entry('Antony', opp)
    # Determine if Antony was outer or inner
    if a_outer == 'Antony':
        # stored as pf1=antony_s, pf2=opp_s
        e['pf1'] = round(e['pf1'] - larson_s, 2)
        e['pf2'] = round(e['pf2'] - opp_s, 2)
        if larson_s > opp_s: e['w1'] -= 1
        else:                 e['w2'] -= 1
    else:
        # Antony was inner, so pf2=antony_s, pf1=opp_s
        e['pf2'] = round(e['pf2'] - larson_s, 2)
        e['pf1'] = round(e['pf1'] - opp_s, 2)
        if larson_s > opp_s: e['w2'] -= 1
        else:                 e['w1'] -= 1
    # Track pairs for seasons decrement
    antony_pairs_fixed.add((a_outer, a_inner))

# Decrement seasons for each affected Antony pair
for (a_outer, a_inner) in antony_pairs_fixed:
    existing[a_outer][a_inner]['seasons'] -= 1
    # If pair now has 0 games, remove it
    e = existing[a_outer][a_inner]
    if e['w1'] + e['w2'] == 0:
        del existing[a_outer][a_inner]
        print(f"  Removed empty pair: {a_outer} vs {a_inner}")

# Clean up empty outer keys
for outer in list(existing.keys()):
    if not existing[outer]:
        del existing[outer]
        print(f"  Removed empty outer key: {outer}")

# Step 2: Add 2019 contributions under Larson pairs
larson_pairs_added = set()
for (wk, opp, larson_s, opp_s) in GAMES_2019_LARSON:
    l_outer, l_inner, e = get_or_create('Larson', opp)
    # Determine orientation
    if l_outer == 'Larson':
        e['pf1'] = round(e['pf1'] + larson_s, 2)
        e['pf2'] = round(e['pf2'] + opp_s, 2)
        if larson_s > opp_s: e['w1'] += 1
        else:                 e['w2'] += 1
        if e['big1'] is None or larson_s > e['big1']: e['big1'] = larson_s
        if e['big2'] is None or opp_s > e['big2']:   e['big2'] = opp_s
        if e['last'] is None:
            winner = 'Larson' if larson_s > opp_s else opp
            e['last'] = {'winner':winner,'score1':larson_s,'score2':opp_s,'season':'19'}
    else:
        # opp is outer, Larson is inner
        e['pf1'] = round(e['pf1'] + opp_s, 2)
        e['pf2'] = round(e['pf2'] + larson_s, 2)
        if opp_s > larson_s: e['w1'] += 1
        else:                 e['w2'] += 1
        if e['big1'] is None or opp_s > e['big1']:    e['big1'] = opp_s
        if e['big2'] is None or larson_s > e['big2']: e['big2'] = larson_s
        if e['last'] is None:
            winner = opp if opp_s > larson_s else 'Larson'
            e['last'] = {'winner':winner,'score1':opp_s,'score2':larson_s,'season':'19'}
    larson_pairs_added.add((l_outer, l_inner))

# Increment seasons for Larson pairs
for (l_outer, l_inner) in larson_pairs_added:
    existing[l_outer][l_inner]['seasons'] += 1

after_count = sum(e['w1']+e['w2'] for d in existing.values() for e in d.values())
print(f"After:  {sum(len(v) for v in existing.values())} pairs, {after_count} games")
print(f"New Larson pairs: {sorted(larson_pairs_added)}")

# ── Rebuild JS ────────────────────────────────────────────────────────────────
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

# Inject back into kdp_report.html
html_new = html[:h2h_start] + out + html[h2h_end:]
# Update footnote
html_new = html_new.replace(
    'Data from 2019–2025 seasons · Historical seasons (2009–2018) compiling',
    'Data from 2019–2025 seasons · Historical seasons (2009–2018) compiling'
)
with open('kdp_report.html','w') as f: f.write(html_new)
print("Done. kdp_report.html and h2h_all.js updated.")
# Spot check Antony vs Kyle2 (should be GONE, they never played 2022-2025 since Kyle2 left)
print("Antony pairs:", sorted(existing.get('Antony',{}).keys()))
print("Larson pairs:", sorted(existing.get('Larson',{}).keys()))
