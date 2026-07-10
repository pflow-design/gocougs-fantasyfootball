// Rebuilds the All-Time Record Book (data/records.json) from the per-season data
// — the single source of truth — so every data-derivable record is computed, not
// curated. ALL seasons 2009-2025 are included (2009 is no longer excluded).
//
//   node scripts/build-records.mjs            # compute + print, no write
//   node scripts/build-records.mjs --write    # also write data/records.json
//
// Regular season only: weeklyScores hold regular-season games; playoffs live
// elsewhere and are excluded here. Player-stat rows (TDs, yardage) and Low Season
// Avg stay curated TBD — they need per-player box scores not in the dataset.

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

const files = readdirSync(resolve(root, 'data/seasons')).filter((f) => f.endsWith('.json'));
const seasons = files.map((f) => readJson('data/seasons/' + f)).sort((a, b) => a.year - b.year);
const CURRENT = Math.max(...seasons.map((s) => s.year)); // 2025

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
      weekScores.push({ year: s.year, key: a, week: w, score: sa });
      weekScores.push({ year: s.year, key: b, week: w, score: sb });
      const wKey = sa >= sb ? a : b, lKey = sa >= sb ? b : a;
      margins.push({ year: s.year, week: w, wKey, lKey, margin: Math.abs(sa - sb) });
      (seq[a] ||= []).push(sa > sb ? 'W' : sa < sb ? 'L' : 'T');
      (seq[b] ||= []).push(sb > sa ? 'W' : sb < sa ? 'L' : 'T');
    }
  }
  for (const [key, arr] of Object.entries(seq)) {
    for (const type of ['W', 'L']) {
      let best = 0, run = 0;
      for (const r of arr) { run = r === type ? run + 1 : 0; if (run > best) best = run; }
      if (best > 0) streaks.push({ year: s.year, key, type, len: best });
    }
  }
  for (const st of s.standings || []) {
    if (!st.managerKey) continue;
    teams.push({ year: s.year, key: st.managerKey, w: st.w, l: st.l, t: st.t || 0, pf: st.pf, pa: st.pa, games: st.games || st.w + st.l + (st.t || 0) });
  }
}

// ---- Selection helpers -----------------------------------------------------
// Integer records tie often -> collect all at the extreme. Float records take
// the single extreme (exact ties are vanishingly unlikely).
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
  return best; // {v, i}
}

// Value formatters (match the report's style).
const pts = (v) => v.toFixed(2);
const comma = (v) => v.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const perWk = (v) => v.toFixed(2) + '/wk';

// Holder builders.
const names2025 = (at) => [...new Set(at.map((i) => D(i.key)))].join(' / ');
function allTimeIntHolder(at) {
  const yrs = [...new Set(at.map((i) => i.year))];
  if (at.length === 1) return { holder: D(at[0].key), season: at[0].year };
  if (yrs.length === 1) return { holder: names2025(at), season: yrs[0] }; // same year, multiple people
  return { holder: at.map((i) => `${D(i.key)} '${yy(i.year)}`).join(' / '), season: null }; // spread across years
}

// ---- Compute each record (2025 row + All-Time row) -------------------------
// vs = single-team-value (wins/losses/streak/points), fmt formats the value.
function intRecord(items, valFn, fmt, max) {
  const cur = pickInt(items, valFn, { max, year: CURRENT });
  const all = pickInt(items, valFn, { max });
  return {
    y2025: { holder: names2025(cur.at), value: fmt(cur.best) },
    allTime: { ...allTimeIntHolder(all.at), value: fmt(all.best) },
  };
}
function floatTeamRecord(items, valFn, fmt, max, { detail } = {}) {
  const cur = pickFloat(items, valFn, { max, year: CURRENT });
  const all = pickFloat(items, valFn, { max });
  return {
    y2025: { holder: D(cur.i.key), ...(detail ? { detail: detail(cur.i) } : {}), value: fmt(cur.v) },
    allTime: { holder: D(all.i.key), season: all.i.year, value: fmt(all.v) },
  };
}
function marginRecord(max) {
  const cur = pickFloat(margins, (m) => m.margin, { max, year: CURRENT });
  const all = pickFloat(margins, (m) => m.margin, { max });
  const vs = (m) => `${D(m.wKey)} vs. ${D(m.lKey)}`;
  return {
    y2025: { holder: vs(cur.i), detail: `Wk ${cur.i.week}`, value: `${pts(cur.v)} pts` },
    allTime: { holder: vs(all.i), season: all.i.year, value: `${pts(all.v)} pts` },
  };
}

const mostWins = intRecord(teams, (t) => t.w, (n) => `${n} W`, true);
const mostLosses = intRecord(teams, (t) => t.l, (n) => `${n} L`, true);
const winStreak = intRecord(streaks.filter((s) => s.type === 'W'), (s) => s.len, (n) => `${n} games`, true);
const lossStreak = intRecord(streaks.filter((s) => s.type === 'L'), (s) => s.len, (n) => `${n} games`, true);

const biggestBlowout = marginRecord(true);
const closestGame = marginRecord(false);
const hardestSched = floatTeamRecord(teams, (t) => t.pa / t.games, perWk, true);
const easiestSched = floatTeamRecord(teams, (t) => t.pa / t.games, perWk, false);

const highWeek = floatTeamRecord(weekScores, (w) => w.score, pts, true, { detail: (w) => `Wk ${w.week}` });
const lowWeek = floatTeamRecord(weekScores, (w) => w.score, pts, false, { detail: (w) => `Wk ${w.week}` });
const highSeason = floatTeamRecord(teams, (t) => t.pf, comma, true);
const lowSeason = floatTeamRecord(teams, (t) => t.pf, comma, false);

// Preserve curated (data-not-available) rows verbatim from the existing file.
const prev = readJson('data/records.json');
const prevRec = (title, metric) => {
  const g = prev.groups.find((x) => x.title === title);
  return g ? g.records.find((r) => r.metric === metric) : null;
};

// ---- Assemble ---------------------------------------------------------------
const out = {
  _meta: {
    title: 'All-Time Record Book — Regular Season',
    description: "Regular season only (playoff games excluded). RECOMPUTED from data/seasons/*.json by scripts/build-records.mjs — every season 2009-2025 is included. Each metric has a '2025' row (current-season leader) and an 'allTime' row (best/worst across all seasons). Player-stat rows and Low Season Avg remain TBD: they need per-player weekly box scores that do not exist in the project.",
    source: 'data/seasons/*.json via scripts/build-records.mjs',
    seasonRowLabelNote: "The '2025' row = the current season's leader; the 'allTime' row = best/worst across all seasons.",
  },
  groups: [
    {
      title: 'Head-to-Head Records', icon: '🏆',
      records: [
        { metric: 'Most Wins', ...mostWins },
        { metric: 'Win Streak', ...winStreak },
        { metric: 'Most Losses', ...mostLosses },
        { metric: 'Loss Streak', ...lossStreak },
      ],
    },
    {
      title: 'Margins of Victory', icon: '💥',
      records: [
        { metric: 'Biggest Blowout', ...biggestBlowout },
        { metric: 'Closest Game', ...closestGame },
        { metric: 'Hardest Schedule', ...hardestSched, definition: 'Average opponent points scored against a manager (Points-Against / games).' },
        { metric: 'Easiest Schedule', ...easiestSched },
      ],
    },
    {
      title: 'Points Records', icon: '📊',
      records: [
        { metric: 'High Single Week', ...highWeek },
        { metric: 'High Season Total', ...highSeason },
        { metric: 'Low Single Week', ...lowWeek },
        { metric: 'Low Season Total', ...lowSeason },
        prevRec('Points Records', 'Low Season Avg (off.)'),
      ],
    },
    // Statistical (player-stat) records: preserved verbatim — box scores not in dataset.
    prev.groups.find((g) => g.title === 'Statistical Records'),
  ],
};

// ---- Report -----------------------------------------------------------------
const line = (r) => {
  const a = r.allTime || {};
  const tag = a.season ? ` '${yy(a.season)}` : '';
  console.log(`  ${r.metric.padEnd(18)} 2025: ${(r.y2025?.holder + (r.y2025?.detail ? ', ' + r.y2025.detail : '')).padEnd(28)} ${String(r.y2025?.value).padStart(12)}   |  All: ${((a.holder ?? '—') + tag).padEnd(32)} ${String(a.value).padStart(12)}`);
};
for (const g of out.groups) { console.log('\n' + g.icon + ' ' + g.title); for (const r of g.records) if (r.y2025 || r.allTime) line(r); }

if (WRITE) {
  writeFileSync(resolve(root, 'data/records.json'), JSON.stringify(out, null, 2) + '\n');
  console.log('\nWROTE data/records.json');
} else {
  console.log('\n(dry run — pass --write to save)');
}
