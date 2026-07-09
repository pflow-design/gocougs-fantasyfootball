// Builds data/seasons/2009.json + 2011..2024.json from the legacy gen_h2h_*.py
// weekly schedules. These SCHED_YYYY dicts are the closest thing to a clean
// per-season weekly dataset (regular season only; playoffs live separately and
// are intentionally NOT used for standings — records are regular-season only).
//
// Run:  node scripts/build-seasons.mjs
//
// Formats handled (see HANDOFF.md section 2):
//   2009:      GAMES_2009 = [(wk, mgrA, mgrB, sA, sB, isPlayoff), ...]   (game list)
//   2011-2022: SCHED_YYYY = {mgr: [(wk, oppKey, own, opp), ...]}
//   2023:      SCHED_2023 = {mgr: [(wk, oppKey, 'W'/'L', own, opp), ...]}
//   2024:      SCHED_2024 = {mgr: [[wk, oppTeamName, 'Win'/'Loss', own, opp], ...]}
//              + TEAM_MGR_2024 to resolve opponent team names to manager keys.
//
// Old keys are normalized to canonical: Kyle->KyleK, Kyle2->KyleP, Ryan->Rudee.
// 2010 has no weekly matchups in the project (only team-season standings in
// scraped_2025_2010.md), so it is not built here.

import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
// Strip Python comments (quote-aware, so '#CougsVsEverybody' survives) so that
// parenthesized text inside comments isn't mistaken for data rows.
function stripComments(src) {
  return src.split('\n').map((line) => {
    let q = null;
    for (let i = 0; i < line.length; i++) {
      const ch = line[i];
      if (q) { if (ch === q) q = null; }
      else if (ch === "'" || ch === '"') q = ch;
      else if (ch === '#') return line.slice(0, i);
    }
    return line;
  }).join('\n');
}
const legacy = (f) => stripComments(readFileSync(resolve(root, 'legacy', f), 'utf8'));

const LEAGUE_ID = {
  2009: '320012', 2011: '554079', 2012: '229595', 2013: '241415', 2014: '372078',
  2015: '443395', 2016: '782767', 2017: '645247', 2018: '857102', 2019: '615427',
  2020: '562876', 2021: '475255', 2022: '302522', 2023: '211296', 2024: '764109',
};
// Champions per season (from legacy headers + docs; see data/champions.json).
const CHAMPION = {
  2009: 'duncan', 2011: 'Antony', 2012: 'duncan', 2013: 'Larson', 2014: 'Antony',
  2015: 'PatrickF', 2016: 'Antony', 2017: 'KyleP', 2018: 'RyanC', 2019: 'duncan',
  2020: 'David', 2021: 'Rudee', 2022: 'Antony', 2023: 'Jeremy', 2024: 'Daniel',
};
const KEY = (k) => ({ Kyle: 'KyleK', Kyle2: 'KyleP', Ryan: 'Rudee' }[k] || k);
const regWeeksFor = (y) => (y <= 2010 ? 13 : y <= 2020 ? 14 : 15);

// 2009 attribution corrections (confirmed by Patrick, 2026-07):
//  - "cougs4bcsbid" was David — the old scripts mislabeled that hidden slot 'Larson'.
//  - "Team Malaysia" ('Irfan Since 05') was a hidden one-off — mislabeled 'David'.
//  - Larson (Robbie) was NOT in the league in 2009.
// Applied to the original GAMES_2009 labels (single lookup, no chaining).
const REMAP_2009 = { Larson: 'David', David: '__IRFAN2009__' };
// 2019 correction (confirmed by Patrick, 2026-07): the hidden scmid=4 team (4-10)
// was mislabeled 'Antony' in SCHED_2019 — it is actually Larson (Robbie). Antony
// was NOT in the league in 2019. legacy/fix_2019_larson.py fixed only the report's
// h2hData, never this source dict, so the builder must remap it here.
const REMAP_2019 = { Antony: 'Larson' };
const HIDDEN_2009 = { __IRFAN2009__: { manager: 'Irfan (hidden)', team: 'Team Malaysia' } };
// 2009 team names by canonical manager key (from gen_h2h_2009.py header).
const TEAMS_2009 = {
  David: 'cougs4bcsbid', Bradley: 'FUCK YOU RUDEE', RyanC: 'Purple Reign',
  Raj: 'Sound Records', Daniel: 'Favre and Away', PatrickF: 'AIDS',
  KyleK: 'Ballcuzzis', duncan: 'The Frying Pans', Antony: 'The Blackouts',
};

// --- Python-literal helpers -------------------------------------------------

// Brace-match a bracket ({ or [) starting at/after `from`, return [text, endIdx].
function matchBracket(src, from, open = '{', close = '}') {
  const start = src.indexOf(open, from);
  let depth = 0;
  for (let i = start; i < src.length; i++) {
    if (src[i] === open) depth++;
    else if (src[i] === close && --depth === 0) return [src.slice(start, i + 1), i];
  }
  throw new Error('Unbalanced ' + open);
}

// Split a tuple/list body on top-level commas, honoring ' and " quotes.
function splitTokens(body) {
  const out = [];
  let cur = '', q = null;
  for (const ch of body) {
    if (q) { cur += ch; if (ch === q) q = null; }
    else if (ch === "'" || ch === '"') { q = ch; cur += ch; }
    else if (ch === ',') { out.push(cur); cur = ''; }
    else cur += ch;
  }
  if (cur.trim() !== '') out.push(cur);
  return out.map(parseToken);
}
function parseToken(t) {
  t = t.trim();
  if (t[0] === "'" || t[0] === '"') return t.slice(1, -1);
  if (t === 'True') return true;
  if (t === 'False') return false;
  return Number(t);
}
// All top-level ( ) or [ ] groups inside a list body (rows have no nested groups).
function parseRows(listText) {
  const rows = [];
  const re = /[([]([^()\[\]]*)[)\]]/g;
  let m;
  while ((m = re.exec(listText))) rows.push(splitTokens(m[1]));
  return rows;
}
// Parse a `NAME = { 'key': [ ... ], ... }` dict into {key: rows[]}.
function parseSchedDict(src, varName) {
  const [obj] = matchBracket(src, src.indexOf(varName), '{', '}');
  const out = {};
  const re = /['"]([^'"]+)['"]\s*:\s*\[/g;
  let m;
  while ((m = re.exec(obj))) {
    const [listText] = matchBracket(obj, m.index + m[0].length - 1, '[', ']');
    out[m[1]] = parseRows(listText);
  }
  return out;
}
// Parse a `NAME = [ ... ]` list variable into rows[].
function parseListVar(src, varName) {
  const re = new RegExp('(?:^|\\n)\\s*' + varName + '\\s*=\\s*\\[');
  const m = re.exec(src);
  if (!m) throw new Error('Could not find list var ' + varName);
  const [listText] = matchBracket(src, m.index + m[0].length - 1, '[', ']');
  return parseRows(listText);
}
// Parse a `NAME = { 'key': VAR_REF, ... }` dict of variable references, then
// resolve each referenced list var. Used for SCHED_2024 (per-team variables).
function parseSchedDictByRef(src, varName) {
  const [obj] = matchBracket(src, src.indexOf(varName + ' ='), '{', '}');
  const out = {};
  const re = /['"]([^'"]+)['"]\s*:\s*([A-Za-z_]\w*)\s*,?/g;
  let m;
  while ((m = re.exec(obj))) out[m[1]] = parseListVar(src, m[2]);
  return out;
}
function parseTeamMap(src, varName) {
  const [obj] = matchBracket(src, src.indexOf(varName), '{', '}');
  const map = {};
  // Backreference \1/\3 so an inner apostrophe (e.g. "Clappin' Cheeks") is kept.
  const re = /(['"])((?:(?!\1).)*)\1\s*:\s*(['"])((?:(?!\3).)*)\3/g;
  let m;
  while ((m = re.exec(obj))) map[m[2]] = m[4];
  return map;
}

// --- Standings + weekly from parsed games ----------------------------------

function blankTeam() { return { w: 0, l: 0, t: 0, pf: 0, pa: 0, games: 0 }; }

// game = {wk, a, b, sa, sb} with canonical keys; credits both sides.
function tallyGame(table, g) {
  for (const [self, own, opp] of [[g.a, g.sa, g.sb], [g.b, g.sb, g.sa]]) {
    const row = (table[self] ||= blankTeam());
    row.pf += own; row.pa += opp; row.games++;
    if (own > opp) row.w++; else if (own < opp) row.l++; else row.t++;
  }
}

function finalize(year, table, weekly, opts = {}) {
  const { hidden = {}, teams = {} } = opts;
  const standings = Object.entries(table)
    .map(([key, r]) => {
      const h = hidden[key];
      const row = {
        manager: h ? h.manager : key,
        managerKey: h ? null : key,
        w: r.w, l: r.l, t: r.t,
        pf: +r.pf.toFixed(2), pa: +r.pa.toFixed(2),
        diff: +(r.pf - r.pa).toFixed(2), games: r.games,
      };
      const team = h ? h.team : teams[key];
      if (team) row.team = team;
      return row;
    })
    .sort((x, y) => y.w - x.w || y.pf - x.pf)
    .map((row, i) => ({ rank: i + 1, ...row }));

  const disp = (k) => (hidden[k] ? hidden[k].team : k);
  const weeklyScores = {};
  for (const wk of Object.keys(weekly).sort((a, b) => a - b)) {
    weeklyScores[wk] = weekly[wk].map((g) => [disp(g.a), g.sa, disp(g.b), g.sb]);
  }
  return {
    _meta: {
      description: `${year} KDP season regular-season standings + weekly results, built from ` +
        `legacy/gen_h2h_${year}.py by scripts/build-seasons.mjs. Standings are regular season only.`,
      source: `legacy/gen_h2h_${year}.py`,
      generatedBy: 'scripts/build-seasons.mjs',
    },
    year,
    leagueId: LEAGUE_ID[year],
    yahooUrl: `https://football.fantasysports.yahoo.com/${year}/f1/${LEAGUE_ID[year]}`,
    teams: standings.length,
    regularSeasonWeeks: regWeeksFor(year),
    champion: CHAMPION[year] ? { managerKey: CHAMPION[year] } : null,
    standings,
    weeklyScores,
  };
}

// Add a matchup to the weekly map, de-duplicated by week + unordered pair.
function addWeekly(weekly, seen, g) {
  const id = g.wk + ':' + [g.a, g.b].sort().join('-');
  if (seen.has(id)) return;
  seen.add(id);
  (weekly[g.wk] ||= []).push(g);
}

function buildFromGames(year, rows, opts = {}) {
  // rows: [wk, mgrA, mgrB, sA, sB, isPlayoff]
  const remap = opts.remap || ((k) => k);
  const table = {}, weekly = {}, seen = new Set();
  for (const [wk, a, b, sa, sb, isPlayoff] of rows) {
    if (isPlayoff) continue; // regular season only
    const g = { wk, a: KEY(remap(a)), b: KEY(remap(b)), sa, sb };
    tallyGame(table, g);
    addWeekly(weekly, seen, g);
  }
  return finalize(year, table, weekly, opts);
}

function buildFromSched(year, dict, { hasResult, teamMap, keyRemap }) {
  const remap = keyRemap || ((k) => k);
  const table = {}, weekly = {}, seen = new Set();
  for (const [mgrRaw, rows] of Object.entries(dict)) {
    const self = KEY(remap(mgrRaw));
    for (const row of rows) {
      // row shapes: [wk,opp,own,opp2] | [wk,opp,result,own,opp2]
      const wk = row[0];
      let oppRaw, own, oppScore;
      if (hasResult) { oppRaw = row[1]; own = row[3]; oppScore = row[4]; }
      else { oppRaw = row[1]; own = row[2]; oppScore = row[3]; }
      const opp = KEY(remap(teamMap ? teamMap[oppRaw] : oppRaw));
      if (!opp) throw new Error(`${year}: could not resolve opponent "${oppRaw}"`);
      const g = { wk, a: self, b: opp, sa: own, sb: oppScore };
      // Tally only from the self side (each manager lists all their own games).
      const rowT = (table[self] ||= blankTeam());
      rowT.pf += own; rowT.pa += oppScore; rowT.games++;
      if (own > oppScore) rowT.w++; else if (own < oppScore) rowT.l++; else rowT.t++;
      addWeekly(weekly, seen, g);
    }
  }
  return finalize(year, table, weekly);
}

// --- Drive all seasons ------------------------------------------------------

const results = [];
function emit(season) {
  const warns = [];
  const rw = season.regularSeasonWeeks;
  for (const s of season.standings) {
    if (s.games !== rw) warns.push(`${s.managerKey} played ${s.games} (expected ${rw})`);
  }
  const dir = resolve(root, 'data/seasons');
  mkdirSync(dir, { recursive: true });
  writeFileSync(resolve(dir, `${season.year}.json`), JSON.stringify(season, null, 2) + '\n');
  const wl = season.standings.reduce((n, s) => n + s.w + s.l + s.t, 0) / 2;
  results.push({ year: season.year, teams: season.teams, games: wl, warns });
}

// 2009 (game list)
{
  const src = legacy('gen_h2h_2009.py');
  const [list] = matchBracket(src, src.indexOf('GAMES_2009'), '[', ']');
  emit(buildFromGames(2009, parseRows(list), {
    remap: (k) => REMAP_2009[k] ?? k,
    hidden: HIDDEN_2009,
    teams: TEAMS_2009,
  }));
}
// 2011-2022 (sched, no result field). 2019 needs the Antony->Larson remap.
for (const y of [2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]) {
  const src = legacy(`gen_h2h_${y}.py`);
  const keyRemap = y === 2019 ? (k) => REMAP_2019[k] ?? k : undefined;
  emit(buildFromSched(y, parseSchedDict(src, `SCHED_${y}`), { hasResult: false, keyRemap }));
}
// 2023 (sched with result field, opp = manager key)
{
  const src = legacy('gen_h2h_2023.py');
  emit(buildFromSched(2023, parseSchedDict(src, 'SCHED_2023'), { hasResult: true }));
}
// 2024 (sched with result field, opp = team name -> manager)
{
  const src = legacy('gen_h2h_2024.py');
  const teamMap = parseTeamMap(src, 'TEAM_MGR_2024');
  emit(buildFromSched(2024, parseSchedDictByRef(src, 'SCHED_2024'), { hasResult: true, teamMap }));
}

// --- Report -----------------------------------------------------------------
console.log('Built seasons:');
for (const r of results) {
  const flag = r.warns.length ? ` ⚠️  ${r.warns.join('; ')}` : ' ✓';
  console.log(`  ${r.year}: ${r.teams} teams, ${r.games} games${flag}`);
}
