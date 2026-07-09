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
const waivers = readJson('data/yahoo-waivers.json').moves;
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
const ordinal = (n) => { const s = ['th', 'st', 'nd', 'rd'], v = n % 100; return n + (s[(v - 20) % 10] || s[v] || s[0]); };
const round = (n) => Math.round(n).toLocaleString('en-US');

// ---- per-season enrichment -------------------------------------------------
const seasonDir = resolve(root, 'data/seasons');
const files = readdirSync(seasonDir).filter((f) => /^(2009|201\d|202[0-4])\.json$/.test(f));
const report = [];

for (const file of files) {
  const year = Number(file.replace('.json', ''));
  const season = readJson(`data/seasons/${file}`);
  const sc = yahoo[year];
  if (!sc) { report.push(`${year}: no scrape`); continue; }

  // Scraped teams; array order == final placement (1st..Nth). Join to the
  // existing standings by W-L record + nearest PF (robust to tiny computed-vs-
  // Yahoo PF differences), then adopt Yahoo's authoritative PF/PA for display.
  const scTeams = sc.teams.map((t, i) => ({
    team: t[0], w: Number(t[1].split('-')[0]), l: Number(t[1].split('-')[1]),
    pf: t[2], pa: t[3], streak: t[4], rating: t[5], level: t[6], finalPlace: i + 1, _used: false,
  }));
  const matchScraped = (row) => {
    let best = null, bd = Infinity;
    for (const s of scTeams) {
      if (s._used || s.w !== row.w || s.l !== row.l) continue;
      const d = Math.abs(s.pf - (row.pf || 0));
      if (d < bd) { bd = d; best = s; }
    }
    if (!best) for (const s of scTeams) { if (s._used) continue; const d = Math.abs(s.pf - (row.pf || 0)); if (d < bd) { bd = d; best = s; } }
    if (best) best._used = true;
    return best;
  };
  const keyToTeam = {};
  for (const row of season.standings) {
    const m = matchScraped(row);
    if (m) {
      row.team = m.team && !m.team.startsWith('__') ? m.team : (row.team ?? display(row.managerKey));
      row.streak = m.streak;
      row.rating = (m.rating && m.rating !== '-') ? Number(m.rating) : null;
      row.level = (m.level && m.level !== '-') ? m.level : null;
      row.finalPlace = m.finalPlace;
      row.waiverMoves = (waivers[year] || {})[m.team] ?? null;
      row.pf = m.pf; row.pa = m.pa; row.diff = +(m.pf - m.pa).toFixed(2); // Yahoo is authoritative
    }
    if (row.managerKey) { row.manager = display(row.managerKey); keyToTeam[row.managerKey] = row.team; } // consistent display names
  }

  // Per-season context for notes/stories.
  const playoffCount = year <= 2010 ? 6 : 4;
  const teamsN = season.standings.length;
  const pfRank = {}, paRank = {};
  [...season.standings].sort((a, b) => b.pf - a.pf).forEach((r, i) => (pfRank[r.team] = i + 1));
  [...season.standings].sort((a, b) => (a.pa ?? 0) - (b.pa ?? 0)).forEach((r, i) => (paRank[r.team] = i + 1));
  const movesVals = season.standings.map((r) => r.waiverMoves).filter((m) => typeof m === 'number');
  const maxMoves = movesVals.length ? Math.max(...movesVals) : null;
  const minMoves = movesVals.length ? Math.min(...movesVals) : null;
  const madePlayoffs = (r) => r.rank <= playoffCount;

  // Contextual profile note.
  const noteFor = (r) => {
    const p = [];
    const fp = r.finalPlace;
    if (fp === 1) p.push('🏆 Champion.');
    else if (fp === 2) p.push('Runner-up.');
    else if (fp === 3) p.push('Third place.');
    else if (madePlayoffs(r)) p.push(`Made the playoffs as the ${ordinal(r.rank)} seed; finished ${ordinal(fp || r.rank)}.`);
    else p.push(`Finished ${ordinal(fp || r.rank)} of ${teamsN}.`);
    const pr = pfRank[r.team];
    let scoring = pr === 1 ? `Led the league in scoring (${round(r.pf)} PF)` : pr === teamsN ? `Fewest points in the league (${round(r.pf)} PF)` : `${ordinal(pr)} in scoring (${round(r.pf)} PF)`;
    if (pr === 1 && fp > 1) scoring += ' — the best team that didn\'t win';
    p.push(scoring + '.');
    const b = badge(r.rating, r.level);
    if (b) p.push(`Yahoo ${b}.`);
    if (typeof r.waiverMoves === 'number') {
      if (r.waiverMoves === maxMoves && maxMoves > 0) p.push(`Worked the waiver wire hardest (${r.waiverMoves} moves).`);
      else if (r.waiverMoves === minMoves) p.push(`Quietest roster in the league (${r.waiverMoves} moves).`);
    }
    return p.join(' ');
  };

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
    note: noteFor(r),
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

  // --- Stories (varied, generated from standings + playoffs + weekly) ---
  const stories = [];
  const wk = season.weeklyScores || {};
  const wkNums = Object.keys(wk).filter((k) => /^\d+$/.test(k));
  const teamOf = (k) => keyToTeam[k] ?? display(k) ?? k;
  const nameOf = (k) => display(k) ?? k;
  const stByPlace = (pl) => season.standings.find((r) => r.finalPlace === pl);
  const champ = champByYear[year];

  // 1. Champion's run
  if (champ?.champion) {
    const cr = stByPlace(1);
    const champTeam = cr?.team ?? (champ.team && !champ.team.startsWith('__') ? champ.team : teamOf(champ.champion));
    const finalG = season.playoffs?.championship?.games?.find((g) => g.label === 'Championship Game');
    let body = `${champTeam} (${nameOf(champ.champion)}) captured the ${year} title`;
    if (cr && madePlayoffs(cr)) body += ` as the ${ordinal(cr.rank)} seed`;
    if (finalG) body += `, beating ${finalG.loser.team} ${finalG.winner.score.toFixed(2)}–${finalG.loser.score.toFixed(2)} in the final`;
    stories.push({ emoji: '🏆', headline: `${nameOf(champ.champion)} hoists the trophy`, body: body + '.' });
  }

  // 2. Best team that didn't win (points leader who fell short)
  const leader = season.standings.find((r) => pfRank[r.team] === 1);
  if (leader && leader.finalPlace !== 1) {
    const where = madePlayoffs(leader) ? `bowed out of the playoffs and finished ${ordinal(leader.finalPlace)}` : `somehow missed the playoffs`;
    stories.push({ emoji: '📈', headline: 'The best team that didn’t win', body: `${leader.team} poured in a league-best ${round(leader.pf)} points but ${where}. Fantasy is cruel.` });
  }

  // 3. Most unlucky (highest scorer to miss the playoffs)
  const missers = season.standings.filter((r) => !madePlayoffs(r)).sort((a, b) => b.pf - a.pf);
  if (missers.length && missers[0].team !== leader?.team) {
    const u = missers[0];
    stories.push({ emoji: '😤', headline: `${u.team}: all points, no luck`, body: `${u.team} scored ${round(u.pf)} — ${ordinal(pfRank[u.team])}-most in the league — yet watched the playoffs from the couch at ${fmtRec(u.w, u.l, u.t)}.` });
  }

  // 4/5. Biggest blowout + closest game (from weekly)
  if (wkNums.length) {
    let blow = null, close = null;
    for (const w of wkNums) for (const [a, sa, b, sb] of wk[w]) {
      const m = Math.abs(sa - sb), win = sa >= sb ? a : b, lose = sa >= sb ? b : a, ws = Math.max(sa, sb), ls = Math.min(sa, sb);
      if (!blow || m > blow.m) blow = { win, lose, ws, ls, m, w };
      if (!close || m < close.m) close = { win, lose, ws, ls, m, w };
    }
    if (blow) stories.push({ emoji: '💥', headline: `Biggest blowout: ${blow.m.toFixed(2)} points`, body: `Week ${blow.w}: ${teamOf(blow.win)} steamrolled ${teamOf(blow.lose)} ${blow.ws.toFixed(2)}–${blow.ls.toFixed(2)}.` });
    if (close) stories.push({ emoji: '⚡', headline: `Down to the wire: ${close.m.toFixed(2)} points`, body: `Week ${close.w} was a nail-biter — ${teamOf(close.win)} slipped past ${teamOf(close.lose)} ${close.ws.toFixed(2)}–${close.ls.toFixed(2)}.` });
  }

  // 6. The basement
  const last = stByPlace(teamsN);
  if (last) {
    let extra = '.';
    if (typeof last.waiverMoves === 'number' && last.waiverMoves === minMoves) extra = ` — and made a league-low ${last.waiverMoves} roster moves all year.`;
    else if (typeof last.waiverMoves === 'number' && last.waiverMoves === maxMoves) extra = ` — despite a league-high ${last.waiverMoves} waiver moves.`;
    else if (pfRank[last.team] === teamsN) extra = ', dead last in scoring too.';
    stories.push({ emoji: '🪣', headline: `${last.team} brings up the rear`, body: `Last place at ${fmtRec(last.w, last.l, last.t)}${extra}` });
  }

  if (stories.length) season.stories = stories.slice(0, 6);

  writeFileSync(resolve(seasonDir, file), JSON.stringify(season, null, 2) + '\n');
  report.push(`${year}: chart✓ profiles(${season.teamProfiles.length}) playoffs(${season.playoffs ? 'Y' : '-'}) stories(${stories.length})`);
}

console.log(report.join('\n'));
