"""
KDP H2H Data Generator - 2025 Season
Generates h2hData JS object for all-time head-to-head comparison tool
"""
from collections import defaultdict
import json

MGRS = ['Raj','duncan','PatrickF','RyanC','David','Kyle','Antony','Daniel','Ryan','Jeremy']

TEAM_MGR_2025 = {
    'RIPete': 'PatrickF',
    'Spoiling Your Cottage Cheese': 'duncan',
    'GIBBS Me Head': 'David',
    'Benching Kelce': 'Kyle',
    'The Cuddly Kittens': 'Antony',
    "Clappin' Cheeks": 'Jeremy',
    'Hit Somebody': 'Ryan',
    'My Ball Zach Ertz': 'Daniel',
    'shmoney maker': 'Raj',
    'Trips Formation': 'RyanC',
}

# [wk, opp_team, W/L, own_score, opp_score]
# Corrections applied: Daniel wk10 Loss (not Win), Jeremy wk14 Loss (not Win)
SCHED_2025 = {
  'PatrickF': [
    [1,'Benching Kelce','L',60.92,130.28],[2,'Hit Somebody','L',116.98,126.48],
    [3,'Trips Formation','W',146.86,102.42],[4,'Spoiling Your Cottage Cheese','L',88.38,98.64],
    [5,'GIBBS Me Head','L',117.90,146.72],[6,'shmoney maker','W',124.68,89.94],
    [7,'My Ball Zach Ertz','W',150.72,80.44],[8,'The Cuddly Kittens','L',129.28,138.78],
    [9,"Clappin' Cheeks",'L',101.98,111.30],[10,'Benching Kelce','W',130.30,122.32],
    [11,'Hit Somebody','L',96.58,98.64],[12,'Trips Formation','L',69.78,140.02],
    [13,'Spoiling Your Cottage Cheese','L',112.94,135.34],[14,'GIBBS Me Head','L',143.84,148.14],
    [15,'shmoney maker','L',143.86,164.70],
  ],
  'duncan': [
    [1,'The Cuddly Kittens','L',91.42,107.44],[2,"Clappin' Cheeks",'L',56.84,109.28],
    [3,'Benching Kelce','L',69.94,104.72],[4,'RIPete','W',98.64,88.38],
    [5,'Trips Formation','L',113.58,115.38],[6,'Hit Somebody','L',92.94,125.46],
    [7,'GIBBS Me Head','L',110.16,142.42],[8,'shmoney maker','W',125.48,113.72],
    [9,'My Ball Zach Ertz','L',90.60,109.22],[10,'The Cuddly Kittens','L',89.30,122.80],
    [11,"Clappin' Cheeks",'L',114.82,148.64],[12,'Benching Kelce','L',101.16,101.82],
    [13,'RIPete','W',135.34,112.94],[14,'Trips Formation','L',105.34,105.36],
    [15,'Hit Somebody','L',139.10,169.80],
  ],
  'David': [
    [1,'My Ball Zach Ertz','L',110.46,123.78],[2,'The Cuddly Kittens','W',93.32,86.38],
    [3,"Clappin' Cheeks",'W',133.22,88.96],[4,'Benching Kelce','L',120.36,159.18],
    [5,'RIPete','W',146.72,117.90],[6,'Trips Formation','L',91.50,105.86],
    [7,'Spoiling Your Cottage Cheese','W',142.42,110.16],[8,'Hit Somebody','L',119.32,125.28],
    [9,'shmoney maker','W',129.72,78.32],[10,'My Ball Zach Ertz','W',120.34,120.12],  # David WON
    [11,'The Cuddly Kittens','W',120.78,119.24],[12,"Clappin' Cheeks",'W',159.32,109.68],
    [13,'Benching Kelce','W',141.92,98.72],[14,'RIPete','W',148.14,143.84],
    [15,'Trips Formation','W',122.82,94.80],
  ],
  'Kyle': [
    [1,'RIPete','W',130.28,60.92],[2,'Trips Formation','W',125.70,109.20],
    [3,'Spoiling Your Cottage Cheese','W',104.72,69.94],[4,'GIBBS Me Head','W',159.18,120.36],
    [5,'shmoney maker','L',96.20,111.34],[6,'My Ball Zach Ertz','L',85.54,103.32],
    [7,'The Cuddly Kittens','L',110.72,153.48],[8,"Clappin' Cheeks",'L',54.08,109.56],
    [9,'Hit Somebody','L',112.74,156.80],[10,'RIPete','L',122.32,130.30],
    [11,'Trips Formation','L',71.00,92.92],[12,'Spoiling Your Cottage Cheese','W',101.82,101.16],
    [13,'GIBBS Me Head','L',98.72,141.92],[14,'shmoney maker','W',94.84,76.42],
    [15,'My Ball Zach Ertz','L',83.02,127.50],
  ],
  'Antony': [
    [1,'Spoiling Your Cottage Cheese','W',107.44,91.42],[2,'GIBBS Me Head','L',86.38,93.32],
    [3,'shmoney maker','L',112.72,114.52],[4,'My Ball Zach Ertz','L',109.02,151.50],
    [5,'Hit Somebody','W',143.62,84.64],[6,"Clappin' Cheeks",'L',122.94,155.48],
    [7,'Benching Kelce','W',153.48,110.72],[8,'RIPete','W',138.78,129.28],
    [9,'Trips Formation','W',120.46,97.06],[10,'Spoiling Your Cottage Cheese','W',122.80,89.30],
    [11,'GIBBS Me Head','L',119.24,120.78],[12,'shmoney maker','W',99.76,91.52],
    [13,'My Ball Zach Ertz','W',97.28,79.10],[14,'Hit Somebody','L',103.46,111.76],
    [15,"Clappin' Cheeks",'L',102.60,113.56],
  ],
  'Jeremy': [
    [1,'Trips Formation','W',133.22,109.26],[2,'Spoiling Your Cottage Cheese','W',109.28,56.84],
    [3,'GIBBS Me Head','L',88.96,133.22],[4,'shmoney maker','W',142.30,101.88],
    [5,'My Ball Zach Ertz','L',100.32,122.00],[6,'The Cuddly Kittens','W',155.48,122.94],
    [7,'Hit Somebody','L',89.44,155.90],[8,'Benching Kelce','W',109.56,54.08],
    [9,'RIPete','W',111.30,101.98],[10,'Trips Formation','L',113.02,116.14],
    [11,'Spoiling Your Cottage Cheese','W',148.64,114.82],[12,'GIBBS Me Head','L',109.68,159.32],
    [13,'shmoney maker','W',147.04,87.72],[14,'My Ball Zach Ertz','L',88.50,117.10],  # Jeremy LOST
    [15,'The Cuddly Kittens','W',113.56,102.60],
  ],
  'Ryan': [
    [1,'shmoney maker','W',95.38,79.12],[2,'RIPete','W',126.48,116.98],
    [3,'My Ball Zach Ertz','L',107.30,116.74],[4,'Trips Formation','L',100.62,126.18],
    [5,'The Cuddly Kittens','L',84.64,143.62],[6,'Spoiling Your Cottage Cheese','W',125.46,92.94],
    [7,"Clappin' Cheeks",'W',155.90,89.44],[8,'GIBBS Me Head','W',125.28,119.32],
    [9,'Benching Kelce','W',156.80,112.74],[10,'shmoney maker','W',119.90,76.24],
    [11,'RIPete','W',98.64,96.58],[12,'My Ball Zach Ertz','L',112.86,159.76],
    [13,'Trips Formation','W',131.44,69.24],[14,'The Cuddly Kittens','W',111.76,103.46],
    [15,'Spoiling Your Cottage Cheese','W',169.80,139.10],
  ],
  'Daniel': [
    [1,'GIBBS Me Head','W',123.78,110.46],[2,'shmoney maker','L',94.64,161.80],
    [3,'Hit Somebody','W',116.74,107.30],[4,'The Cuddly Kittens','W',151.50,109.02],
    [5,"Clappin' Cheeks",'W',122.00,100.32],[6,'Benching Kelce','W',103.32,85.54],
    [7,'RIPete','L',80.44,150.72],[8,'Trips Formation','L',121.96,168.56],
    [9,'Spoiling Your Cottage Cheese','W',109.22,90.60],[10,'GIBBS Me Head','L',120.12,120.34],  # Daniel LOST
    [11,'shmoney maker','W',96.50,62.76],[12,'Hit Somebody','W',159.76,112.86],
    [13,'The Cuddly Kittens','L',79.10,97.28],[14,"Clappin' Cheeks",'W',117.10,88.50],  # Daniel WON
    [15,'Benching Kelce','W',127.50,83.02],
  ],
  'Raj': [
    [1,'Hit Somebody','L',79.12,95.38],[2,'My Ball Zach Ertz','W',161.80,94.64],
    [3,'The Cuddly Kittens','W',114.52,112.72],[4,"Clappin' Cheeks",'L',101.88,142.30],
    [5,'Benching Kelce','W',111.34,96.20],[6,'RIPete','L',89.94,124.68],
    [7,'Trips Formation','W',102.14,95.86],[8,'Spoiling Your Cottage Cheese','L',113.72,125.48],
    [9,'GIBBS Me Head','L',78.32,129.72],[10,'Hit Somebody','L',76.24,119.90],
    [11,'My Ball Zach Ertz','L',62.76,96.50],[12,'The Cuddly Kittens','L',91.52,99.76],
    [13,"Clappin' Cheeks",'L',87.72,147.04],[14,'Benching Kelce','L',76.42,94.84],
    [15,'RIPete','W',164.70,143.86],
  ],
  'RyanC': [
    [1,"Clappin' Cheeks",'L',109.26,133.22],[2,'Benching Kelce','L',109.20,125.70],
    [3,'RIPete','L',102.42,146.86],[4,'Hit Somebody','W',126.18,100.62],
    [5,'Spoiling Your Cottage Cheese','W',115.38,113.58],[6,'GIBBS Me Head','W',105.86,91.50],
    [7,'shmoney maker','L',95.86,102.14],[8,'My Ball Zach Ertz','W',168.56,121.96],
    [9,'The Cuddly Kittens','L',97.06,120.46],[10,"Clappin' Cheeks",'W',116.14,113.02],
    [11,'Benching Kelce','W',92.92,71.00],[12,'RIPete','W',140.02,69.78],
    [13,'Hit Somebody','L',69.24,131.44],[14,'Spoiling Your Cottage Cheese','W',105.36,105.34],
    [15,'GIBBS Me Head','L',94.80,122.82],
  ],
}

# Playoff matchups for 2025 (mgr_a, mgr_b, score_a, score_b)
PLAYOFFS_2025 = [
    ('David',  'Jeremy', 104.30, 129.52),  # SF1
    ('Ryan',   'Daniel', 151.30, 175.30),  # SF2
    ('Daniel', 'Jeremy', 105.00, 113.78),  # Final
    ('David',  'Ryan',    79.58, 161.72),  # 3rd place
]

def get_key(a, b):
    return (a, b) if a < b else (b, a)

# Build cumulative H2H across seasons
# Structure: h2h_totals[(a,b)] = {w_a, w_b, pf_a, pf_b, matches:[(yr,wk,s_a,s_b,playoff)], last_yr, last_wk}
h2h = defaultdict(lambda: {
    'w_a': 0, 'w_b': 0, 'pf_a': 0.0, 'pf_b': 0.0,
    'matches': [], 'playoffs': 0
})

def process_season(schedules, team_mgr, year, playoffs, reg_season_weeks=15):
    """Process one season's schedules and add to h2h"""
    seen = set()  # (wk, mgr_a, mgr_b) to avoid double-counting
    
    for mgr, sched in schedules.items():
        for row in sched:
            wk, opp_team, result, s1, s2 = row[0], row[1], row[2], row[3], row[4]
            opp_mgr = team_mgr[opp_team]
            key = get_key(mgr, opp_mgr)
            dedup_key = (year, wk, key[0], key[1])
            if dedup_key in seen:
                continue
            seen.add(dedup_key)
            
            a, b = key
            is_a = (mgr == a)
            if is_a:
                sa, sb = s1, s2
                won_a = (result == 'W')
            else:
                sa, sb = s2, s1
                won_a = (result == 'L')
            
            if won_a:
                h2h[key]['w_a'] += 1
            else:
                h2h[key]['w_b'] += 1
            h2h[key]['pf_a'] += sa
            h2h[key]['pf_b'] += sb
            h2h[key]['matches'].append((year, wk, sa, sb, False))
    
    # Playoffs
    for mgr_a, mgr_b, sa, sb in playoffs:
        key = get_key(mgr_a, mgr_b)
        a, b = key
        if mgr_a == a:
            won_a = sa > sb
            pf_a, pf_b = sa, sb
        else:
            won_a = sb > sa
            pf_a, pf_b = sb, sa
        if won_a:
            h2h[key]['w_a'] += 1
        else:
            h2h[key]['w_b'] += 1
        h2h[key]['pf_a'] += pf_a
        h2h[key]['pf_b'] += pf_b
        h2h[key]['playoffs'] += 1
        h2h[key]['matches'].append((2025, 'PO', pf_a, pf_b, True))

process_season(SCHED_2025, TEAM_MGR_2025, 2025, PLAYOFFS_2025)

# Verify totals
total_wins = sum(d['w_a']+d['w_b'] for d in h2h.values())
print(f"Total wins/losses recorded: {total_wins} (expected 75 reg + 4 playoff = 79)")

# Print all pairs
print("\n=== 2025 H2H SUMMARY ===")
for key in sorted(h2h.keys()):
    a, b = key
    d = h2h[key]
    print(f"{a} {d['w_a']}-{d['w_b']} {b} | PF {d['pf_a']:.2f}-{d['pf_b']:.2f} | {d['w_a']+d['w_b']} games | {d['playoffs']} playoffs")

# Generate JavaScript h2hData object
# Format: h2hData['A']['B'] = {w1, w2, pf1, pf2, big1, big2, last, playoffs, seasons}
# where w1 = wins by first manager in MANAGERS key order
print("\n\n=== GENERATING JS h2hData ===")

def make_h2h_entry(a, b):
    """a and b are manager keys (canonical ordering)"""
    key = get_key(a, b)
    ka, kb = key
    d = h2h.get(key)
    if not d or (d['w_a'] + d['w_b']) == 0:
        return None
    
    # a's stats vs b
    if a == ka:
        wa, wb = d['w_a'], d['w_b']
        pfa, pfb = d['pf_a'], d['pf_b']
        matches = [(yr, wk, sa, sb, po) for yr, wk, sa, sb, po in d['matches']]
    else:
        wa, wb = d['w_b'], d['w_a']
        pfa, pfb = d['pf_b'], d['pf_a']
        matches = [(yr, wk, sb, sa, po) for yr, wk, sa, sb, po in d['matches']]
    
    # Biggest wins for each
    big_a = max((sa for yr, wk, sa, sb, po in matches if sa > sb), default=None)
    big_b = max((sb for yr, wk, sa, sb, po in matches if sb > sa), default=None)
    
    # Last matchup
    reg_matches = [(yr, wk, sa, sb, po) for yr, wk, sa, sb, po in matches if not po]
    po_matches = [(yr, wk, sa, sb, po) for yr, wk, sa, sb, po in matches if po]
    all_matches = sorted(matches, key=lambda x: (x[0], 99 if x[1]=='PO' else x[1]), reverse=True)
    last = all_matches[0] if all_matches else None
    
    seasons_25 = 1 if matches else 0
    
    return {
        'w1': wa, 'w2': wb,
        'pf1': round(pfa, 2), 'pf2': round(pfb, 2),
        'big1': big_a, 'big2': big_b,
        'last': {'winner': a if last[2] > last[3] else b, 
                 'score1': last[2], 'score2': last[3],
                 'season': str(last[0])[-2:]} if last else None,
        'playoffs': d['playoffs'],
        'seasons': seasons_25,
    }

# Build the JS object
js_lines = ['var h2hData = {']
for a in MGRS:
    entries = {}
    for b in MGRS:
        if b <= a: continue
        entry = make_h2h_entry(a, b)
        if entry:
            entries[b] = entry
    if entries:
        js_lines.append(f"  '{a}': {{")
        for b, e in entries.items():
            big1 = f"{e['big1']:.2f}" if e['big1'] else 'null'
            big2 = f"{e['big2']:.2f}" if e['big2'] else 'null'
            last = 'null'
            if e['last']:
                l = e['last']
                last = f"{{winner:'{l['winner']}',score1:{l['score1']},score2:{l['score2']},season:'{l['season']}'}}"
            js_lines.append(f"    '{b}': {{w1:{e['w1']},w2:{e['w2']},pf1:{e['pf1']},pf2:{e['pf2']},big1:{big1},big2:{big2},last:{last},playoffs:{e['playoffs']},seasons:{e['seasons']}}},")
        js_lines[-1] = js_lines[-1].rstrip(',')
        js_lines.append('  },')

js_lines.append('};')
js_output = '\n'.join(js_lines)
print(js_output[:2000])

with open('/sessions/elegant-eloquent-hamilton/mnt/outputs/h2h_2025.js', 'w') as f:
    f.write(js_output)
print(f"\nSaved to h2h_2025.js")

