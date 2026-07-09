// Enriches every season (2009-2024) with the four rich sections that 2025 has:
// PF-vs-PA chart, Team Profiles (with Yahoo badges), Playoff Results, and
// auto-generated Stories. Scraped Yahoo data (team names, PA, badges, final
// placements) lives in data/yahoo-seasons.json; it's joined to the existing,
// validated per-season standings by PF (a unique key), so no manager-name
// disambiguation is needed. Playoff games come from the legacy PLAYOFFS_YYYY /
// GAMES_2009 blocks. Stories are computed from weeklyScores.
//
//   node scripts/enrich-seasons.mjs
//
// 2025 is left as-is (already rich). 2010 is standings-only (no weekly), so it
// gets chart + profiles but limited playoffs/stories.

import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const readJson = (p) => JSON.parse(readFileSync(resolve(root, p), 'utf8'));
const legacyRaw = (f) => readFileSync(resolve(root, 'legacy', f), 'utf8');

const yahoo = readJson('data/yahoo-seasons.json').seasons;
const champions = readJson('data/champions.json');
const managers = readJson('data/managers.json').managers;
const champByYear = {};
for (const c of champions.byYear) champByYear[c.year] = c;
const display = (key) => managers.find((m) => m.key === key)?.display ?? key;

// ---- legacy playoff parsing (minimal, mirrors recompute.mjs) ----------------
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
const legacy = (f) => stripComments(legacyRaw(f));
function matchBracket(src, from, open, close) {
  const start = src.indexOf(open, from);
  let depth = 0;
  for (let i = start; i < src.length; i++) {
    if (src[i] === open) depth++;
    else if (src[i] === close && --depth === 0) return src.slice(start, i + 1);
  }
  throw new Error('unbalanced');
}
function splitTokens(body) {
  const out = []; let cur = '', q = null;
  for (const ch of body) {
    if (q) { cur += ch; if (ch === q) q = null; }
    else if (ch === "'" || ch === '"') { q = ch; cur += ch; }
    else if (ch === ',') { out.push(cur); cur = ''; }
    else cur += ch;
  }
  if (cur.trim() !== '') out.push(cur);
  return out.map((t) => {
    t = t.trim();
    if (t[0] === "'" || t[0] === '"') return t.slice(1, -1);
    if (t === 'True') return true;
    if (t === 'False') return false;
    return Number(t);
  });
}
function parseRows(listText) {
  const rows = []; const re = /[([]([^()\[\]]*)[)\]]/g; let m;
  while ((m = re.exec(listText))) rows.push(splitTokens(m[1]));
  return rows;
}
function parseListVar(src, name) {
  const m = new RegExp('(?:^|\\n)\\s*' + name + '\\s*=\\s*\\[').exec(src);
  if (!m) return [];
  return parseRows(matchBracket(src, m.index + m[0].length - 1, '[', ']'));
}
const KEY = (k) => ({ Kyle: 'KyleK', Kyle2: 'KyleP', Ryan: 'Rudee' }[k] || k);
const REMAP_2009 = { Larson: 'David', David: 'Irfan' };
const REMAP_2019 = { Antony: 'Larson' };

// Returns [{week, a, b, sa, sb}] of playoff games with canonical keys.
function playoffGames(year) {
  if (year === 2009) {
    const src = legacy('gen_h2h_2009.py');
    const rows = parseRows(matchBracket(src, src.indexOf('GAMES_2009'), '[', ']'));
    return rows.filter((r) => r[5] === true).map(([wk, a, b, sa, sb]) => ({
      week: wk, a: KEY(REMAP_2009[a] ?? a), b: KEY(REMAP_2009[b] ?? b), sa, sb,
    })).filter((g) => g.a !== 'Irfan' && g.b !== 'Irfan');
  }
  if (year === 2010) return [];
  const src = legacy(`gen_h2h_${year}.py`);
  const rows = parseListVar(src, `PLAYOFFS_${year}`);
  const rm = year === 2019 ? (k) => REMAP_2019[k] ?? k : (k) => k;
  return rows.map((r) => {
    if (r.length >= 6) return { week: r[0], a: KEY(rm(r[1])), b: KEY(rm(r[2])), sa: r[3], sb: r[4] };
    return { week: null, a: KEY(rm(r[0])), b: KEY(rm(r[1])), sa: r[2], sb: r[3] }; // 2023/2024 4-tuple
  });
}

// ---- helpers ---------------------------------------------------------------
const fmtRec = (w, l, t) => `${w}-${l}-${t || 0}`;
const badge = (rating, level) => (rating && rating !== '-' && level && level !== '-') ? `${level} ${rating}` : null;

// ---- per-season enrichment -------------------------------------------------
const seasonDir = resolve(root, 'data/seasons');
const files = readdirSync(seasonDir).filter((f) => /^(2009|201\d|202[0-4])\.json$/.test(f));
const report = [];

for (const file of files) {
  const year = Number(file.replace('.json', ''));
  const season = readJson(`data/seasons/${file}`);
  const sc = yahoo[year];
  if (!sc) { report.push(`${year}: no scrape`); continue; }

  // Scraped lookups. Order of sc.teams == final placement (1st..Nth).
  const byPf = new Map();       // pf(2dp) -> scraped tuple + finalPlace
  const byTeamNorm = new Map(); // normalized team -> scraped tuple
  const norm = (s) => (s || '').toLowerCase().replace(/[^a-z0-9]/g, '');
  sc.teams.forEach((t, i) => {
    const rec = { team: t[0], wlt: t[1], pf: t[2], pa: t[3], streak: t[4], rating: t[5], level: t[6], finalPlace: i + 1 };
    byPf.set(t[2].toFixed(2), rec);
    byTeamNorm.set(norm(t[0]), rec);
  });

  // Join scraped -> existing standings by PF (2010 has no weekly PF match issues:
  // its standings PF were rounded, so match 2010 by team name instead).
  const keyToTeam = {};
  for (const row of season.standings) {
    let match = byPf.get((row.pf || 0).toFixed(2));
    if (!match && row.team) match = byTeamNorm.get(norm(row.team));
    if (match) {
      row.team = match.team && match.team !== '__DAVID_BLOCKED__' ? match.team : (row.team ?? display(row.managerKey));
      row.streak = match.streak;
      row.rating = (match.rating && match.rating !== '-') ? Number(match.rating) : null;
      row.level = (match.level && match.level !== '-') ? match.level : null;
      row.finalPlace = match.finalPlace;
      if (year === 2010) { row.pf = match.pf; row.pa = match.pa; row.diff = +(match.pf - match.pa).toFixed(2); }
    }
    if (row.managerKey) keyToTeam[row.managerKey] = row.team;
  }

  // --- PF/PA chart (ordered by PF desc, manager display labels) ---
  const chartRows = [...season.standings].sort((a, b) => b.pf - a.pf);
  season.pfpaChart = {
    teams: chartRows.map((r) => display(r.managerKey) ?? r.team),
    pf: chartRows.map((r) => +r.pf.toFixed(2)),
    pa: chartRows.map((r) => +(r.pa ?? 0).toFixed(2)),
  };

  // --- Team Profiles (ordered by final placement) ---
  const profiled = [...season.standings]
    .filter((r) => r.finalPlace)
    .sort((a, b) => a.finalPlace - b.finalPlace);
  const rest = season.standings.filter((r) => !r.finalPlace);
  season.teamProfiles = [...profiled, ...rest].map((r) => ({
    team: r.team ?? display(r.managerKey),
    manager: display(r.managerKey) ?? r.manager ?? 'hidden',
    record: fmtRec(r.w, r.l, r.t),
    place: r.finalPlace ?? null,
    badges: [r.finalPlace === 1 ? `${year} CHAMPION` : null, badge(r.rating, r.level)].filter(Boolean),
    pf: +r.pf.toFixed(2),
    pa: +(r.pa ?? 0).toFixed(2),
    diff: +((r.pf) - (r.pa ?? 0)).toFixed(2),
  }));

  // --- Playoffs (championship bracket only) ---
  const pg = playoffGames(year);
  if (pg.length) {
    const champKey = champByYear[year]?.champion;
    const playoffCount = year <= 2010 ? 6 : 4;
    const seeds = new Set(season.standings.filter((r) => r.rank <= playoffCount && r.managerKey).map((r) => r.managerKey));
    // Championship bracket = games between playoff seeds (drops the consolation bracket).
    const champBracket = pg.filter((g) => seeds.has(g.a) && seeds.has(g.b));
    const gTeam = (k) => keyToTeam[k] ?? display(k);
    const toGame = (g, label) => {
      const aWin = g.sa >= g.sb;
      return { label, winner: { team: gTeam(aWin ? g.a : g.b), score: aWin ? g.sa : g.sb }, loser: { team: gTeam(aWin ? g.b : g.a), score: aWin ? g.sb : g.sa } };
    };
    const weeks = [...new Set(champBracket.map((g) => g.week).filter((w) => w != null))].sort((a, b) => a - b);
    let semis = [], finals = [], finalWeek = null;
    if (weeks.length) {
      finalWeek = weeks[weeks.length - 1];
      const fw = champBracket.filter((g) => g.week === finalWeek);
      const earlier = champBracket.filter((g) => g.week !== finalWeek);
      const champGame = fw.find((g) => g.a === champKey || g.b === champKey);
      const thirdGame = fw.find((g) => g !== champGame);
      if (champGame) finals.push(toGame(champGame, 'Championship Game'));
      if (thirdGame) finals.push(toGame(thirdGame, '3rd Place Game'));
      semis = earlier.map((g, i) => toGame(g, `Semifinal ${i + 1}`));
    } else {
      // 2023/2024: 4-tuples, no week; legacy order is [SF1, SF2, Final, 3rd].
      if (champBracket[0]) semis.push(toGame(champBracket[0], 'Semifinal 1'));
      if (champBracket[1]) semis.push(toGame(champBracket[1], 'Semifinal 2'));
      if (champBracket[2]) finals.push(toGame(champBracket[2], 'Championship Game'));
      if (champBracket[3]) finals.push(toGame(champBracket[3], '3rd Place Game'));
    }
    season.playoffs = {};
    if (semis.length) season.playoffs.semifinals = { week: weeks[0] ?? null, games: semis };
    if (finals.length) season.playoffs.championship = { week: finalWeek, games: finals };
  }

  // --- Stories (generated from weeklyScores + standings) ---
  const stories = [];
  const wk = season.weeklyScores || {};
  const wkNums = Object.keys(wk).filter((k) => /^\d+$/.test(k));
  const teamOf = (k) => keyToTeam[k] ?? display(k) ?? k;
  const nameOf = (k) => display(k) ?? k;
  if (wkNums.length) {
    let hi = null, lo = null, blow = null, close = null;
    for (const w of wkNums) {
      for (const [a, sa, b, sb] of wk[w]) {
        for (const [k, s] of [[a, sa], [b, sb]]) {
          if (!hi || s > hi.s) hi = { k, s, w };
          if (!lo || s < lo.s) lo = { k, s, w };
        }
        const m = Math.abs(sa - sb);
        const win = sa >= sb ? a : b, ws = Math.max(sa, sb), ls = Math.min(sa, sb), lose = sa >= sb ? b : a;
        if (!blow || m > blow.m) blow = { win, lose, ws, ls, m, w };
        if (!close || m < close.m) close = { win, lose, ws, ls, m, w };
      }
    }
    if (hi) stories.push({ emoji: '🔥', headline: `Highest week: ${nameOf(hi.k)} — ${hi.s.toFixed(2)}`, body: `${teamOf(hi.k)} posted the season's top single-week score, ${hi.s.toFixed(2)} points in Week ${hi.w}.` });
    if (blow) stories.push({ emoji: '💥', headline: `Biggest blowout: ${blow.m.toFixed(2)} pts`, body: `In Week ${blow.w}, ${teamOf(blow.win)} crushed ${teamOf(blow.lose)} ${blow.ws.toFixed(2)}–${blow.ls.toFixed(2)}, a ${blow.m.toFixed(2)}-point margin.` });
    if (close) stories.push({ emoji: '⚡', headline: `Closest game: ${close.m.toFixed(2)} pts`, body: `Week ${close.w} came down to ${close.m.toFixed(2)}: ${teamOf(close.win)} edged ${teamOf(close.lose)} ${close.ws.toFixed(2)}–${close.ls.toFixed(2)}.` });
    if (lo) stories.push({ emoji: '😬', headline: `Lowest week: ${nameOf(lo.k)} — ${lo.s.toFixed(2)}`, body: `${teamOf(lo.k)} bottomed out at ${lo.s.toFixed(2)} in Week ${lo.w} — the season's lowest.` });
  }
  const champ = champByYear[year];
  if (champ?.champion) {
    const ct = champ.team && !champ.team.startsWith('__') ? champ.team : teamOf(champ.champion);
    stories.push({ emoji: '🏆', headline: `${nameOf(champ.champion)} wins it all`, body: `${ct} took the ${year} title${champ.runnerUp ? `, beating ${nameOf(champ.runnerUp)} in the final` : ''}.` });
  }
  if (stories.length) season.stories = stories;

  writeFileSync(resolve(seasonDir, file), JSON.stringify(season, null, 2) + '\n');
  report.push(`${year}: chart✓ profiles(${season.teamProfiles.length}) playoffs(${season.playoffs ? 'Y' : '-'}) stories(${stories.length})`);
}

console.log(report.join('\n'));
