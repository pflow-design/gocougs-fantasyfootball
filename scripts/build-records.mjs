// Rebuilds the All-Time Record Book (data/records.json) from the per-season data.
// Every data-derivable record is computed for ALL seasons 2009-2025 (an `allTime`
// mark plus a `bySeason` map), so the Records page can default to all-time and
// offer a season selector. Player-stat rows and Low Season Avg stay curated TBD
// (they need per-player box scores not in the dataset).
//
//   node scripts/build-records.mjs            # compute + print, no write
//   node scripts/build-records.mjs --write    # also write data/records.json
//
// Regular season only (weeklyScores hold regular-season games; playoffs are
// excluded here). Steven abandoned his 2010 team mid-season, so his scores, team
// rows and games are dropped from every record (EXCLUDE below).

import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const WRITE = process.argv.includes('--write');
const readJson = (p) => JSON.parse(readFileSync(resolve(root, p), 'utf8'));

const managersDoc = readJson('data/managers.json');
const disp = Object.fromEntries(managersDoc.managers.map((m) => [m.key, m.display]));
const D = (k) => disp[k] || k;
const yy = (y) => String(y).slice(-2);

// Managers disqualified from the Record Book (abandoned teams). See notes above.
const EXCLUDE = new Set(['Steven']);

const files = readdirSync(resolve(root, 'data/seasons')).filter((f) => f.endsWith('.json'));
const seasons = files.map((f) => readJson('data/seasons/' + f)).sort((a, b) => a.year - b.year);
const YEARS = seasons.map((s) => s.year);

// ---- Primitive collections -------------------------------------------------
const weekScores = []; // {year, key, week, score}
const margins = [];    // {year, week, wKey, lKey, margin}
const teams = [];      // {year, key, w, l, t, pf, pa, games}
const streaks = [];    // {year, key, type:'W'|'L', len}

for (const s of seasons) {
  const wk = s.weeklyScores || {};
  const weeks = Object.keys(wk).filter((k) => /^\d+$/.test(k)).map(Number).sort((a, b) => a - b);
  const seq = {}; // key -> ['W'|'L'|'T', ...] in week order
  for (const w of weeks) {
    for (const [a, sa, b, sb] of wk[String(w)]) {
      if (!EXCLUDE.has(a)) weekScores.push({ year: s.year, key: a, week: w, score: sa });
      if (!EXCLUDE.has(b)) weekScores.push({ year: s.year, key: b, week: w, score: sb });
      const wKey = sa >= sb ? a : b, lKey = sa >= sb ? b : a;
      if (!EXCLUDE.has(wKey) && !EXCLUDE.has(lKey)) margins.push({ year: s.year, week: w, wKey, lKey, margin: Math.abs(sa - sb) });
      if (!EXCLUDE.has(a)) (seq[a] ||= []).push(sa > sb ? 'W' : sa < sb ? 'L' : 'T');
      if (!EXCLUDE.has(b)) (seq[b] ||= []).push(sb > sa ? 'W' : sb < sa ? 'L' : 'T');
    }
  }
  for (const [key, arr] of Object.entries(seq)) for (const type of ['W', 'L']) {
    let best = 0, run = 0;
    for (const r of arr) { run = r === type ? run + 1 : 0; if (run > best) best = run; }
    if (best > 0) streaks.push({ year: s.year, key, type, len: best });
  }
  for (const st of s.standings || []) {
    if (!st.managerKey || EXCLUDE.has(st.managerKey)) continue;
    teams.push({ year: s.year, key: st.managerKey, w: st.w, l: st.l, t: st.t || 0, pf: st.pf, pa: st.pa, games: st.games || st.w + st.l + (st.t || 0) });
  }
}

// ---- Selection helpers -----------------------------------------------------
function pickInt(items, valFn, { max = true, year = null } = {}) {
  const pool = year ? items.filter((i) => i.year === year) : items;
  let best = max ? -Infinity : Infinity;
  for (const i of pool) { const v = valFn(i); if (max ? v > best : v < best) best = v; }
  return { best, at: pool.filter((i) => valFn(i) === best) };
}
function pickFloat(items, valFn, { max = true, year = null } = {}) {
  const pool = year ? items.filter((i) => i.year === year) : items;
  let best = null;
  for (const i of pool) { const v = valFn(i); if (best === null || (max ? v > best.v : v < best.v)) best = { v, i }; }
  return best; // {v, i} | null
}

const pts = (v) => v.toFixed(2);
const comma = (v) => v.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const perWk = (v) => v.toFixed(2) + '/wk';
const names = (at) => [...new Set(at.map((i) => D(i.key)))].join(' / ');
function allTimeInt(at) {
  const yrs = [...new Set(at.map((i) => i.year))];
  if (at.length === 1) return { holder: D(at[0].key), season: at[0].year };
  if (yrs.length === 1) return { holder: names(at), season: yrs[0] };
  return { holder: at.map((i) => `${D(i.key)} '${yy(i.year)}`).join(' / '), season: null };
}

// ---- Record builders (allTime + bySeason) ----------------------------------
function intRecord(items, valFn, fmt, max) {
  const all = pickInt(items, valFn, { max });
  const bySeason = {};
  for (const y of YEARS) { const p = pickInt(items, valFn, { max, year: y }); if (p.at.length) bySeason[y] = { holder: names(p.at), value: fmt(p.best) }; }
  return { allTime: { ...allTimeInt(all.at), value: fmt(all.best) }, bySeason };
}
function floatRecord(items, valFn, fmt, max, detail) {
  const all = pickFloat(items, valFn, { max });
  const bySeason = {};
  for (const y of YEARS) { const p = pickFloat(items, valFn, { max, year: y }); if (p) bySeason[y] = { holder: D(p.i.key), ...(detail ? { detail: detail(p.i) } : {}), value: fmt(p.v) }; }
  return { allTime: { holder: D(all.i.key), season: all.i.year, value: fmt(all.v) }, bySeason };
}
function marginRecord(max) {
  const vs = (m) => `${D(m.wKey)} vs. ${D(m.lKey)}`;
  const all = pickFloat(margins, (m) => m.margin, { max });
  const bySeason = {};
  for (const y of YEARS) { const p = pickFloat(margins, (m) => m.margin, { max, year: y }); if (p) bySeason[y] = { holder: vs(p.i), detail: `Wk ${p.i.week}`, value: `${pts(p.v)} pts` }; }
  return { allTime: { holder: vs(all.i), season: all.i.year, value: `${pts(all.v)} pts` }, bySeason };
}

// Curated rows — data not in the project (per-player box scores). TBD stays TBD.
const TBD = { holder: 'TBD', value: 'TBD' };
const curated = {
  lowSeasonAvg: { metric: 'Low Season Avg (off.)', allTime: { ...TBD }, bySeason: {}, curated: true },
  tds: { metric: 'Most TDs (week)', allTime: { ...TBD }, bySeason: { '2025': { holder: 'Raj', detail: 'Wk 15', value: '13 TDs' } }, note: "2025's 13 TDs ties the all-time record set in 2020.", curated: true },
  rush: { metric: 'Rush Yds (week)', allTime: { ...TBD }, bySeason: { '2025': { holder: 'TBD', value: 'TBD' } }, curated: true },
  rec: { metric: 'Rec Yds (week)', allTime: { ...TBD }, bySeason: { '2025': { holder: 'Ryan C', detail: 'Wk 12', value: '608 yds' } }, curated: true },
  pass: { metric: 'Pass Yds (week)', allTime: { ...TBD }, bySeason: { '2025': { holder: 'Patrick', detail: 'Wk 11', value: '452 yds' } }, curated: true },
};

// ---- Assemble ---------------------------------------------------------------
const out = {
  _meta: {
    title: 'All-Time Record Book — Regular Season',
    description: "Regular season only (playoff games excluded). RECOMPUTED from data/seasons/*.json by scripts/build-records.mjs. Each metric has an `allTime` mark and a `bySeason` map (every season 2009-2025) so the Records page defaults to all-time with a season selector. Steven (abandoned his 2010 team mid-season) is EXCLUDED from all records. Player-stat rows and Low Season Avg stay curated TBD (no per-player box scores in the dataset).",
    source: 'data/seasons/*.json via scripts/build-records.mjs',
  },
  years: YEARS,
  groups: [
    {
      title: 'Head-to-Head Records', icon: '🏆',
      records: [
        { metric: 'Most Wins', ...intRecord(teams, (t) => t.w, (n) => `${n} W`, true) },
        { metric: 'Win Streak', ...intRecord(streaks.filter((s) => s.type === 'W'), (s) => s.len, (n) => `${n} games`, true) },
        { metric: 'Most Losses', ...intRecord(teams, (t) => t.l, (n) => `${n} L`, true) },
        { metric: 'Loss Streak', ...intRecord(streaks.filter((s) => s.type === 'L'), (s) => s.len, (n) => `${n} games`, true) },
      ],
    },
    {
      title: 'Margins of Victory', icon: '💥',
      records: [
        { metric: 'Biggest Blowout', ...marginRecord(true) },
        { metric: 'Closest Game', ...marginRecord(false) },
        { metric: 'Hardest Schedule', ...floatRecord(teams, (t) => t.pa / t.games, perWk, true), definition: 'Average opponent points scored against a manager (Points-Against / games).' },
        { metric: 'Easiest Schedule', ...floatRecord(teams, (t) => t.pa / t.games, perWk, false) },
      ],
    },
    {
      title: 'Points Records', icon: '📊',
      records: [
        { metric: 'High Single Week', ...floatRecord(weekScores, (w) => w.score, pts, true, (w) => `Wk ${w.week}`) },
        { metric: 'High Season Total', ...floatRecord(teams, (t) => t.pf, comma, true) },
        { metric: 'Low Single Week', ...floatRecord(weekScores, (w) => w.score, pts, false, (w) => `Wk ${w.week}`) },
        { metric: 'Low Season Total', ...floatRecord(teams, (t) => t.pf, comma, false) },
        curated.lowSeasonAvg,
      ],
    },
    {
      title: 'Statistical Records', icon: '🏈',
      note: 'All-time player-stat rows are TBD: they require per-player weekly box scores across all 16 seasons (~2,000 Yahoo pages), deliberately deferred.',
      records: [curated.tds, curated.rush, curated.rec, curated.pass],
    },
  ],
};

// ---- Report -----------------------------------------------------------------
for (const g of out.groups) {
  console.log('\n' + g.icon + ' ' + g.title);
  for (const r of g.records) {
    const a = r.allTime, tag = a && a.season ? ` '${yy(a.season)}` : '';
    const seasonsCovered = Object.keys(r.bySeason).length;
    console.log(`  ${r.metric.padEnd(20)} all-time: ${((a ? a.holder : '—') + tag).padEnd(34)} ${String(a ? a.value : '—').padStart(12)}   (${seasonsCovered} season rows)`);
  }
}

if (WRITE) {
  writeFileSync(resolve(root, 'data/records.json'), JSON.stringify(out, null, 2) + '\n');
  console.log('\nWROTE data/records.json');
} else {
  console.log('\n(dry run — pass --write to save)');
}
