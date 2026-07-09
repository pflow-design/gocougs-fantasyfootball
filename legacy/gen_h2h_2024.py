"""
KDP H2H Data Generator - 2024 + 2025 Seasons Combined
Generates merged h2hData JS object
"""
from collections import defaultdict

MGRS = ['Raj','duncan','PatrickF','RyanC','David','Kyle','Antony','Daniel','Ryan','Jeremy']

# ── 2024 season ──────────────────────────────────────────────────────────────
TEAM_MGR_2024 = {
    'Virtual Wreckage': 'duncan',
    'Breece Mode': 'Kyle',
    '#CougsVsEverybody': 'David',
    "Clappin' Cheeks": 'Jeremy',
    'Hit Somebody': 'Ryan',
    'RIPete': 'PatrickF',
    'My Ball Zach Ertz': 'Daniel',
    'Chasing Points': 'Antony',
    'shmoney maker': 'Raj',
    'Trips Formation': 'RyanC',
}

# scmid=1 Virtual Wreckage (duncan) 7-8
SCHED_2024_VW = [
    [1,'Trips Formation','Loss',108.16,111.14],[2,'Chasing Points','Win',145.90,99.44],
    [3,'#CougsVsEverybody','Loss',71.60,108.18],[4,'Breece Mode','Win',94.70,71.72],
    [5,'RIPete','Loss',100.64,127.82],[6,"Clappin' Cheeks",'Win',114.68,112.70],
    [7,'Hit Somebody','Win',121.54,80.34],[8,'My Ball Zach Ertz','Win',131.10,110.60],
    [9,'shmoney maker','Loss',125.64,160.80],[10,'Trips Formation','Loss',92.18,97.74],
    [11,'Chasing Points','Loss',94.18,148.24],[12,'#CougsVsEverybody','Win',141.92,68.60],
    [13,'Breece Mode','Win',117.56,112.12],[14,'RIPete','Loss',113.52,125.86],
    [15,"Clappin' Cheeks",'Loss',122.80,149.88],
]
# scmid=2 Breece Mode (Kyle) 6-9
SCHED_2024_BM = [
    [1,"Clappin' Cheeks",'Win',98.12,92.68],[2,'Hit Somebody','Win',133.72,106.02],
    [3,'My Ball Zach Ertz','Loss',88.04,121.68],[4,'Virtual Wreckage','Loss',71.72,94.70],
    [5,'Trips Formation','Loss',96.16,124.94],[6,'Chasing Points','Loss',125.16,125.36],
    [7,'#CougsVsEverybody','Win',119.16,75.80],[8,'shmoney maker','Win',146.44,109.12],
    [9,'RIPete','Loss',110.00,119.50],[10,"Clappin' Cheeks",'Loss',110.18,124.92],
    [11,'Hit Somebody','Win',121.44,96.04],[12,'My Ball Zach Ertz','Loss',86.76,148.36],
    [13,'Virtual Wreckage','Loss',112.12,117.56],[14,'Trips Formation','Win',136.72,71.00],
    [15,'Chasing Points','Loss',100.50,130.44],
]
# scmid=3 #CougsVsEverybody (David) 3-12
SCHED_2024_CVE = [
    [1,'Hit Somebody','Loss',87.58,88.26],[2,'My Ball Zach Ertz','Loss',118.24,126.16],
    [3,'Virtual Wreckage','Win',108.18,71.60],[4,'Trips Formation','Loss',84.58,107.90],
    [5,'Chasing Points','Loss',114.50,143.46],[6,'shmoney maker','Loss',97.26,113.30],
    [7,'Breece Mode','Loss',75.80,119.16],[8,'RIPete','Win',126.28,119.78],
    [9,"Clappin' Cheeks",'Loss',99.84,121.20],[10,'Hit Somebody','Loss',57.54,117.12],
    [11,'My Ball Zach Ertz','Loss',114.18,124.98],[12,'Virtual Wreckage','Loss',68.60,141.92],
    [13,'Trips Formation','Loss',99.28,123.94],[14,'Chasing Points','Loss',120.56,130.44],
    [15,'shmoney maker','Win',113.66,94.78],
]
# scmid=4 Clappin' Cheeks (Jeremy) 10-5
SCHED_2024_CC = [
    [1,'Breece Mode','Loss',92.68,98.12],[2,'RIPete','Win',146.96,110.88],
    [3,'shmoney maker','Win',126.08,104.74],[4,'Hit Somebody','Loss',109.10,147.68],
    [5,'My Ball Zach Ertz','Loss',103.66,123.54],[6,'Virtual Wreckage','Loss',112.70,114.68],
    [7,'Trips Formation','Win',132.90,104.68],[8,'Chasing Points','Win',136.90,111.94],
    [9,'#CougsVsEverybody','Win',121.20,99.84],[10,'Breece Mode','Win',124.92,110.18],
    [11,'RIPete','Win',149.26,97.68],[12,'shmoney maker','Win',105.46,105.22],
    [13,'Hit Somebody','Win',109.90,89.46],[14,'My Ball Zach Ertz','Loss',132.50,132.78],
    [15,'Virtual Wreckage','Win',149.88,122.80],
]
# scmid=5 Hit Somebody (Ryan) 9-6
SCHED_2024_HS = [
    [1,'#CougsVsEverybody','Win',88.26,87.58],[2,'Breece Mode','Loss',106.02,133.72],
    [3,'RIPete','Loss',84.56,121.08],[4,"Clappin' Cheeks",'Win',147.68,109.10],
    [5,'shmoney maker','Win',129.78,97.24],[6,'My Ball Zach Ertz','Win',105.12,85.10],
    [7,'Virtual Wreckage','Loss',80.34,121.54],[8,'Trips Formation','Win',111.16,93.54],
    [9,'Chasing Points','Win',124.14,110.06],[10,'#CougsVsEverybody','Win',117.12,57.54],
    [11,'Breece Mode','Loss',96.04,121.44],[12,'RIPete','Loss',122.18,127.88],
    [13,"Clappin' Cheeks",'Loss',89.46,109.90],[14,'shmoney maker','Win',156.16,137.48],
    [15,'My Ball Zach Ertz','Win',132.64,98.34],
]
# scmid=6 RIPete (PatrickF) 11-4
SCHED_2024_RIP = [
    [1,'shmoney maker','Win',133.12,119.98],[2,"Clappin' Cheeks",'Loss',110.88,146.96],
    [3,'Hit Somebody','Win',121.08,84.56],[4,'My Ball Zach Ertz','Loss',109.94,114.44],
    [5,'Virtual Wreckage','Win',127.82,100.64],[6,'Trips Formation','Win',123.52,108.50],
    [7,'Chasing Points','Win',134.34,110.64],[8,'#CougsVsEverybody','Loss',119.78,126.28],
    [9,'Breece Mode','Win',119.50,110.00],[10,'shmoney maker','Win',131.60,93.30],
    [11,"Clappin' Cheeks",'Loss',97.68,149.26],[12,'Hit Somebody','Win',127.88,122.18],
    [13,'My Ball Zach Ertz','Win',147.18,106.50],[14,'Virtual Wreckage','Win',125.86,113.52],
    [15,'Trips Formation','Win',172.60,90.46],
]
# scmid=7 My Ball Zach Ertz (Daniel) 9-6
SCHED_2024_MBZE = [
    [1,'Chasing Points','Win',127.68,109.30],[2,'#CougsVsEverybody','Win',126.16,118.24],
    [3,'Breece Mode','Win',121.68,88.04],[4,'RIPete','Win',114.44,109.94],
    [5,"Clappin' Cheeks",'Win',123.54,103.66],[6,'Hit Somebody','Loss',85.10,105.12],
    [7,'shmoney maker','Win',101.68,81.62],[8,'Virtual Wreckage','Loss',110.60,131.10],
    [9,'Trips Formation','Loss',109.90,126.24],[10,'Chasing Points','Loss',85.30,134.38],
    [11,'#CougsVsEverybody','Win',124.98,114.18],[12,'Breece Mode','Win',148.36,86.76],
    [13,'RIPete','Loss',106.50,147.18],[14,"Clappin' Cheeks",'Win',132.78,132.50],
    [15,'Hit Somebody','Loss',98.34,132.64],
]
# scmid=8 Chasing Points (Antony) 7-8
SCHED_2024_CP = [
    [1,'My Ball Zach Ertz','Loss',109.30,127.68],[2,'Virtual Wreckage','Loss',99.44,145.90],
    [3,'Trips Formation','Loss',106.94,115.48],[4,'shmoney maker','Loss',107.62,110.50],
    [5,'#CougsVsEverybody','Win',143.46,114.50],[6,'Breece Mode','Win',125.36,125.16],
    [7,'RIPete','Loss',110.64,134.34],[8,"Clappin' Cheeks",'Loss',111.94,136.90],
    [9,'Hit Somebody','Loss',110.06,124.14],[10,'My Ball Zach Ertz','Win',134.38,85.30],
    [11,'Virtual Wreckage','Win',148.24,94.18],[12,'Trips Formation','Loss',109.10,118.06],
    [13,'shmoney maker','Win',157.24,100.32],[14,'#CougsVsEverybody','Win',130.44,120.56],
    [15,'Breece Mode','Win',130.44,100.50],
]
# scmid=9 shmoney maker (Raj) 3-12
SCHED_2024_SM = [
    [1,'RIPete','Loss',119.98,133.12],[2,'Trips Formation','Loss',76.96,81.04],
    [3,"Clappin' Cheeks",'Loss',104.74,126.08],[4,'Chasing Points','Win',110.50,107.62],
    [5,'Hit Somebody','Loss',97.24,129.78],[6,'#CougsVsEverybody','Win',113.30,97.26],
    [7,'My Ball Zach Ertz','Loss',81.62,101.68],[8,'Breece Mode','Loss',109.12,146.44],
    [9,'Virtual Wreckage','Win',160.80,125.64],[10,'RIPete','Loss',93.30,131.60],
    [11,'Trips Formation','Loss',92.68,142.94],[12,"Clappin' Cheeks",'Loss',105.22,105.46],
    [13,'Chasing Points','Loss',100.32,157.24],[14,'Hit Somebody','Loss',137.48,156.16],
    [15,'#CougsVsEverybody','Loss',94.78,113.66],
]
# scmid=10 Trips Formation (RyanC) 10-5
SCHED_2024_TF = [
    [1,'Virtual Wreckage','Win',111.14,108.16],[2,'shmoney maker','Win',81.04,76.96],
    [3,'Chasing Points','Win',115.48,106.94],[4,'#CougsVsEverybody','Win',107.90,84.58],
    [5,'Breece Mode','Win',124.94,96.16],[6,'RIPete','Loss',108.50,123.52],
    [7,"Clappin' Cheeks",'Loss',104.68,132.90],[8,'Hit Somebody','Loss',93.54,111.16],
    [9,'My Ball Zach Ertz','Win',126.24,109.90],[10,'Virtual Wreckage','Win',97.74,92.18],
    [11,'shmoney maker','Win',142.94,92.68],[12,'Chasing Points','Win',118.06,109.10],
    [13,'#CougsVsEverybody','Win',123.94,99.28],[14,'Breece Mode','Loss',71.00,136.72],
    [15,'RIPete','Loss',90.46,172.60],
]

SCHED_2024 = {
    'duncan':  SCHED_2024_VW,
    'Kyle':    SCHED_2024_BM,
    'David':   SCHED_2024_CVE,
    'Jeremy':  SCHED_2024_CC,
    'Ryan':    SCHED_2024_HS,
    'PatrickF':SCHED_2024_RIP,
    'Daniel':  SCHED_2024_MBZE,
    'Antony':  SCHED_2024_CP,
    'Raj':     SCHED_2024_SM,
    'RyanC':   SCHED_2024_TF,
}

# 2024 Playoffs - Championship bracket (4 teams)
# Wk16 SF1: PatrickF(seed1) 135.28 vs Daniel(seed4) 165.94 → Daniel wins
# Wk16 SF2: Jeremy(seed2) 158.02 vs RyanC(seed3) 122.04 → Jeremy wins
# Wk17 Final: Jeremy 142.06 vs Daniel 147.88 → Daniel wins 🏆
# Wk17 3rd: PatrickF 108.32 vs RyanC 144.58 → RyanC wins
# Consolation bracket (4 teams)
# Wk16 C1: duncan 137.12 vs Antony 175.02 → Antony wins
# Wk16 C2: Kyle 94.74 vs Ryan 105.88 → Ryan wins
# Wk17 C3: duncan 119.76 vs Kyle 126.62 → Kyle wins
# Wk17 C4: Ryan 102.78 vs Antony 118.58 → Antony wins
PLAYOFFS_2024 = [
    ('PatrickF','Daniel', 135.28, 165.94),  # SF1 wk16
    ('Jeremy',  'RyanC',  158.02, 122.04),  # SF2 wk16
    ('Jeremy',  'Daniel', 142.06, 147.88),  # Final wk17
    ('PatrickF','RyanC',  108.32, 144.58),  # 3rd place wk17
    ('duncan',  'Antony', 137.12, 175.02),  # Consolation SF wk16
    ('Kyle',    'Ryan',    94.74, 105.88),  # Consolation SF wk16
    ('duncan',  'Kyle',   119.76, 126.62),  # Consolation 3rd wk17
    ('Ryan',    'Antony', 102.78, 118.58),  # Consolation Final wk17
]

# ── 2025 season ──────────────────────────────────────────────────────────────
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
    [9,'shmoney maker','W',129.72,78.32],[10,'My Ball Zach Ertz','W',120.34,120.12],
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
    [13,'shmoney maker','W',147.04,87.72],[14,'My Ball Zach Ertz','L',88.50,117.10],
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
    [9,'Spoiling Your Cottage Cheese','W',109.22,90.60],[10,'GIBBS Me Head','L',120.12,120.34],
    [11,'shmoney maker','W',96.50,62.76],[12,'Hit Somebody','W',159.76,112.86],
    [13,'The Cuddly Kittens','L',79.10,97.28],[14,"Clappin' Cheeks",'W',117.10,88.50],
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

# 2025 Playoffs (championship bracket only - 4 teams)
# SF Wk16: David(1) 104.30 vs Jeremy(4) 129.52 → Jeremy wins
# SF Wk16: Ryan(2) 151.30 vs Daniel(3) 175.30 → Daniel wins
# Final Wk17: Daniel 105.00 vs Jeremy 113.78 → Jeremy wins 🏆
# 3rd Wk17: David 79.58 vs Ryan 161.72 → Ryan wins
PLAYOFFS_2025 = [
    ('David',   'Jeremy', 104.30, 129.52),
    ('Ryan',    'Daniel', 151.30, 175.30),
    ('Daniel',  'Jeremy', 105.00, 113.78),
    ('David',   'Ryan',    79.58, 161.72),
]

# ── H2H accumulator ──────────────────────────────────────────────────────────
h2h = defaultdict(lambda: {
    'w_a': 0, 'w_b': 0, 'pf_a': 0.0, 'pf_b': 0.0,
    'matches': [], 'playoffs': 0
})

def get_key(a, b):
    return (a, b) if a < b else (b, a)

def map_team(team_name, team_mgr):
    """Resolve team name to manager, handling 2025's Win/Loss/Tie field for sched entries"""
    return team_mgr.get(team_name)

def process_season(sched_by_mgr, team_mgr, year, playoffs):
    seen = set()
    for mgr, sched in sched_by_mgr.items():
        for row in sched:
            wk = row[0]; opp_team = row[1]; result = row[2]; s1 = row[3]; s2 = row[4]
            opp_mgr = team_mgr.get(opp_team)
            if not opp_mgr:
                print(f"WARNING: unmapped team '{opp_team}' in {year}")
                continue
            key = get_key(mgr, opp_mgr)
            dedup = (year, wk, key[0], key[1])
            if dedup in seen:
                continue
            seen.add(dedup)
            a, b = key
            is_a = (mgr == a)
            if is_a:
                sa, sb = s1, s2
                won_a = (result in ('W','Win'))
            else:
                sa, sb = s2, s1
                won_a = (result in ('L','Loss'))
            if won_a:
                h2h[key]['w_a'] += 1
            else:
                h2h[key]['w_b'] += 1
            h2h[key]['pf_a'] += sa
            h2h[key]['pf_b'] += sb
            h2h[key]['matches'].append((year, wk, sa, sb, False))

    for mgr_a, mgr_b, sa, sb in playoffs:
        key = get_key(mgr_a, mgr_b)
        a, b = key
        if mgr_a == a:
            won_a = sa > sb; pf_a, pf_b = sa, sb
        else:
            won_a = sb > sa; pf_a, pf_b = sb, sa
        if won_a:
            h2h[key]['w_a'] += 1
        else:
            h2h[key]['w_b'] += 1
        h2h[key]['pf_a'] += pf_a
        h2h[key]['pf_b'] += pf_b
        h2h[key]['playoffs'] += 1
        h2h[key]['matches'].append((year, 'PO', pf_a, pf_b, True))

# Process both seasons
process_season(SCHED_2024, TEAM_MGR_2024, 2024, PLAYOFFS_2024)
process_season(SCHED_2025, TEAM_MGR_2025, 2025, PLAYOFFS_2025)

# Validation
total_wins_2024 = sum(1 for key,d in h2h.items() for m in d['matches'] if m[0]==2024)
total_wins_2025 = sum(1 for key,d in h2h.items() for m in d['matches'] if m[0]==2025)
print(f"2024 matchups: {total_wins_2024} (expect 75 reg + 8 playoff = 83)")
print(f"2025 matchups: {total_wins_2025} (expect 75 reg + 4 playoff = 79)")
print(f"Total matchups across both seasons: {total_wins_2024 + total_wins_2025}")

# Verify 2024 total wins
wins_2024 = sum(d['w_a']+d['w_b'] for d in h2h.values() if any(m[0]==2024 for m in d['matches']))
print(f"2024 total wins: {wins_2024}")  # Hard to compute directly from h2h, just print summary

# ── Build JS output ──────────────────────────────────────────────────────────
def make_entry(a, b):
    key = get_key(a, b)
    ka, kb = key
    d = h2h.get(key)
    if not d or (d['w_a'] + d['w_b']) == 0:
        return None
    if a == ka:
        wa, wb = d['w_a'], d['w_b']
        pfa, pfb = d['pf_a'], d['pf_b']
        matches = [(yr, wk, sa, sb, po) for yr, wk, sa, sb, po in d['matches']]
    else:
        wa, wb = d['w_b'], d['w_a']
        pfa, pfb = d['pf_b'], d['pf_a']
        matches = [(yr, wk, sb, sa, po) for yr, wk, sa, sb, po in d['matches']]

    big_a = max((sa for yr, wk, sa, sb, po in matches if sa > sb), default=None)
    big_b = max((sb for yr, wk, sa, sb, po in matches if sb > sa), default=None)

    all_m = sorted(matches, key=lambda x: (x[0], 99 if x[1]=='PO' else x[1]), reverse=True)
    last = all_m[0] if all_m else None

    seasons = len(set(m[0] for m in matches))

    return {
        'w1': wa, 'w2': wb,
        'pf1': round(pfa, 2), 'pf2': round(pfb, 2),
        'big1': round(big_a, 2) if big_a else None,
        'big2': round(big_b, 2) if big_b else None,
        'last': {
            'winner': a if last[2] > last[3] else b,
            'score1': last[2], 'score2': last[3],
            'season': str(last[0])[-2:]
        } if last else None,
        'playoffs': d['playoffs'],
        'seasons': seasons,
    }

js_lines = ['var h2hData = {']
for a in MGRS:
    entries = {}
    for b in MGRS:
        if b <= a: continue
        e = make_entry(a, b)
        if e:
            entries[b] = e
    if entries:
        js_lines.append(f"  '{a}': {{")
        items = list(entries.items())
        for i, (b, e) in enumerate(items):
            b1 = f"{e['big1']:.2f}" if e['big1'] else 'null'
            b2 = f"{e['big2']:.2f}" if e['big2'] else 'null'
            last = 'null'
            if e['last']:
                l = e['last']
                last = f"{{winner:'{l['winner']}',score1:{l['score1']},score2:{l['score2']},season:'{l['season']}'}}"
            comma = ',' if i < len(items)-1 else ''
            js_lines.append(f"    '{b}': {{w1:{e['w1']},w2:{e['w2']},pf1:{e['pf1']},pf2:{e['pf2']},big1:{b1},big2:{b2},last:{last},playoffs:{e['playoffs']},seasons:{e['seasons']}}}{comma}")
        js_lines.append('  },')

js_lines.append('};')
js_output = '\n'.join(js_lines)

outpath = '/sessions/elegant-eloquent-hamilton/mnt/outputs/h2h_2024_2025.js'
with open(outpath, 'w') as f:
    f.write(js_output)
print(f"\nSaved {len(js_output)} chars to h2h_2024_2025.js")
print("\nFirst 2000 chars:")
print(js_output[:2000])
