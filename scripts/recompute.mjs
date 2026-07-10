// Recomputes all-time manager records + pairwise H2H from the CORRECTED season
// data (the single source of truth), superseding the report-derived aggregates
// that predated the 2009/2010 corrections.
//
//   node scripts/recompute.mjs            # validate only: compute + diff, no writes
//   node scripts/recompute.mjs --write    # also write managers.json + h2h.json
//
// Regular-season games come from data/seasons/*.json (already corrected: David =
// cougs4bcsbid, Team Malaysia = hidden, Larson absent 2009). Playoff games are
// parsed from the legacy files + 2025 season file so H2H (which includes
// playoffs) is complete. 2010 is standings-only (no games) but counts toward
// all-time W-L/PF/seasons and playoff appearances.

import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const WRITE = process.argv.includes('--write');
const readJson = (p) => JSON.parse(readFileSync(resolve(root, p), 'utf8'));

// ---- Python-literal parsing (shared with build-seasons.mjs) ----------------
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
function matchBracket(src, from, open, close) {
  const start = src.indexOf(open, from);
  let depth = 0;
  for (let i = start; i < src.length; i++) {
    if (src[i] === open) depth++;
    else if (src[i] === close && --depth === 0) return [src.slice(start, i + 1), i];
  }
  throw new Error('Unbalanced ' + open);
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
  return parseRows(matchBracket(src, m.index + m[0].length - 1, '[', ']')[0]);
}

const KEY = (k) => ({ Kyle: 'KyleK', Kyle2: 'KyleP', Ryan: 'Rudee' }[k] || k);
const REMAP_2009 = { Larson: 'David', David: '__IRFAN2009__' };
const REMAP_2019 = { Antony: 'Larson' }; // hidden 2019 team mislabeled Antony = Larson
const REMAP_2011 = { Larson: 'KyleP' };  // hidden 2011 'liverpoolsucks69' mislabeled Larson = Kyle P
const twoDigit = (y) => String(y).slice(-2);
const playoffCutoff = (y) => (y <= 2010 ? 6 : 4);

// ---- Load data -------------------------------------------------------------
const managersDoc = readJson('data/managers.json');
const champDoc = readJson('data/champions.json');
const currentH2H = readJson('data/h2h.json');
const KNOWN = new Set(managersDoc.managers.map((m) => m.key));

const seasonFiles = readdirSync(resolve(root, 'data/seasons')).filter((f) => f.endsWith('.json'));
const seasons = seasonFiles.map((f) => readJson('data/seasons/' + f)).sort((a, b) => a.year - b.year);

// Champions (complete) → titles per manager. Prefer byYear if it has all 17.
const byYear = champDoc.byYear || [];
const titleCount = {};
for (const c of byYear) if (c.champion) titleCount[c.champion] = (titleCount[c.champion] || 0) + 1;

// ---- Collect all games (reg from season files, playoffs from legacy) -------
const games = []; // {season, week, playoff, a, b, sa, sb}
const addGame = (season, week, playoff, a, b, sa, sb) => {
  if (!KNOWN.has(a) || !KNOWN.has(b) || a === b) return; // skip hidden/unknown
  games.push({ season, week, playoff, a, b, sa, sb });
};

// Regular season from corrected season files.
for (const s of seasons) {
  const wk = s.weeklyScores || {};
  for (const k of Object.keys(wk)) {
    if (!/^\d+$/.test(k)) continue;
    for (const [a, sa, b, sb] of wk[k]) addGame(s.year, Number(k), false, a, b, sa, sb);
  }
}
// Playoffs — 2009 (from GAMES_2009 is_playoff rows, with 2009 remap).
{
  const src = legacy('gen_h2h_2009.py');
  for (const r of parseRows(matchBracket(src, src.indexOf('GAMES_2009'), '[', ']')[0])) {
    const [wk, a, b, sa, sb, isP] = r;
    if (!isP) continue;
    addGame(2009, wk, true, KEY(REMAP_2009[a] ?? a), KEY(REMAP_2009[b] ?? b), sa, sb);
  }
}
// Playoffs — 2011..2022 (6-tuple: wk,A,B,sA,sB,True).
for (const y of [2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022]) {
  const rmap = y === 2011 ? REMAP_2011 : y === 2019 ? REMAP_2019 : null;
  const rm = rmap ? (k) => rmap[k] ?? k : (k) => k;
  for (const r of parseListVar(legacy(`gen_h2h_${y}.py`), `PLAYOFFS_${y}`)) {
    const [wk, a, b, sa, sb] = r;
    addGame(y, wk, true, KEY(rm(a)), KEY(rm(b)), sa, sb);
  }
}
// Playoffs — 2023, 2024 (4-tuple: A,B,sA,sB; no week).
for (const y of [2023, 2024]) {
  for (const r of parseListVar(legacy(`gen_h2h_${y}.py`), `PLAYOFFS_${y}`)) {
    const [a, b, sa, sb] = r;
    addGame(y, 99, true, KEY(a), KEY(b), sa, sb);
  }
}
// Playoffs — 2025 (from season file; map team -> managerKey).
{
  const s2025 = seasons.find((s) => s.year === 2025);
  const teamKey = {};
  for (const st of s2025.standings) if (st.team && st.managerKey) teamKey[st.team] = st.managerKey;
  const po = s2025.playoffs || {};
  for (const grp of Object.values(po)) {
    for (const g of grp.games) {
      const wk = grp.week ?? 99;
      addGame(2025, wk, true, teamKey[g.winner.team], teamKey[g.loser.team], g.winner.score, g.loser.score);
    }
  }
}

// ---- All-time manager records (regular season) -----------------------------
const roster = {}; // key -> Set(seasonYears in league)
const allTime = {};
const ensure = (k) => (allTime[k] ||= { seasons: 0, w: 0, l: 0, t: 0, pf: 0, pa: 0, playoffAppearances: 0 });
for (const s of seasons) {
  const cut = playoffCutoff(s.year);
  for (const st of s.standings) {
    if (!st.managerKey) continue;
    (roster[st.managerKey] ||= new Set()).add(s.year);
    const r = ensure(st.managerKey);
    r.w += st.w; r.l += st.l; r.t += st.t || 0;
    r.pf += st.pf || 0; r.pa += st.pa || 0;
    if (st.rank <= cut) r.playoffAppearances++;
  }
}
for (const k of Object.keys(allTime)) {
  allTime[k].seasons = roster[k].size;
  allTime[k].titles = titleCount[k] || 0;
  const g = allTime[k].w + allTime[k].l;
  allTime[k].winPct = g ? +((allTime[k].w / g) * 100).toFixed(1) : 0;
  allTime[k].pf = +allTime[k].pf.toFixed(2);
  allTime[k].pa = +allTime[k].pa.toFixed(2);
}

// ---- Pairwise H2H ----------------------------------------------------------
const h2h = {};
const seasonsMet = {}; // "k1|k2" -> Set(season)
for (const g of games) {
  const [k1, k2] = [g.a, g.b].sort();
  const first = g.a === k1; // is side A the primary key?
  (h2h[k1] ||= {});
  const p = (h2h[k1][k2] ||= { w1: 0, w2: 0, pf1: 0, pf2: 0, big1: 0, big2: 0, bigS1: null, bigS2: null, last: null, playoffs: 0, seasons: 0 });
  const s1 = first ? g.sa : g.sb; // primary key's score
  const s2 = first ? g.sb : g.sa;
  p.pf1 += s1; p.pf2 += s2;
  const margin = s1 - s2;
  // big1/big2 = the largest MARGIN (points gap) in a win by that manager; bigS = season of that game.
  if (margin > 0) { p.w1++; if (margin > p.big1) { p.big1 = margin; p.bigS1 = twoDigit(g.season); } }
  else if (margin < 0) { p.w2++; if (-margin > p.big2) { p.big2 = -margin; p.bigS2 = twoDigit(g.season); } }
  if (g.playoff) p.playoffs++;
  (seasonsMet[k1 + '|' + k2] ||= new Set()).add(g.season);
  const cur = p.last;
  const rank = g.season * 100 + g.week;
  if (!cur || rank >= cur._rank) {
    p.last = { winner: margin >= 0 ? k1 : k2, score1: s1, score2: s2, season: twoDigit(g.season), _rank: rank };
  }
}
let pairCount = 0;
for (const k1 of Object.keys(h2h)) for (const k2 of Object.keys(h2h[k1])) {
  const p = h2h[k1][k2];
  p.seasons = seasonsMet[k1 + '|' + k2].size;
  p.pf1 = +p.pf1.toFixed(2); p.pf2 = +p.pf2.toFixed(2);
  p.big1 = +p.big1.toFixed(2); p.big2 = +p.big2.toFixed(2);
  if (p.last) delete p.last._rank;
  pairCount++;
}

// ---- Validation vs current (report) values ---------------------------------
function getCur(a, b) {
  const H = currentH2H.h2h;
  if (H[a] && H[a][b]) return { d: H[a][b], flip: false };
  if (H[b] && H[b][a]) return { d: H[b][a], flip: true };
  return null;
}
console.log(`Games collected: ${games.length} (reg ${games.filter((g) => !g.playoff).length}, playoff ${games.filter((g) => g.playoff).length})`);
console.log(`Managers: ${Object.keys(allTime).length}, H2H pairs: ${pairCount}\n`);

console.log('== All-time manager records (recomputed vs report) ==');
console.log('key        seasons  W-L      winf%   PO  titles   | report W-L / seasons / titles');
for (const m of managersDoc.managers) {
  const a = allTime[m.key];
  if (!a) { console.log(`${m.key.padEnd(10)} (no games/standings found)`); continue; }
  const rep = m.allTime;
  const flag = a.w !== rep.w || a.l !== rep.l || a.seasons !== rep.seasons || a.titles !== rep.titles ? ' *' : '';
  console.log(
    `${m.key.padEnd(10)} ${String(a.seasons).padStart(2)}     ${(a.w + '-' + a.l).padEnd(8)} ${String(a.winPct).padStart(5)} ${String(a.playoffAppearances).padStart(3)} ${String(a.titles).padStart(4)}     | ${rep.w}-${rep.l} / ${rep.seasons} / ${rep.titles}${flag}`
  );
}

console.log('\n== H2H fidelity check: recomputed vs report (w/pf/playoffs), pairs WITHOUT David/Larson ==');
let checked = 0, mism = 0;
for (const k1 of Object.keys(h2h)) for (const k2 of Object.keys(h2h[k1])) {
  if ([k1, k2].some((k) => k === 'David' || k === 'Larson')) continue;
  const cur = getCur(k1, k2);
  if (!cur) { console.log(`  ${k1}-${k2}: no report entry`); continue; }
  const p = h2h[k1][k2];
  const rw1 = cur.flip ? cur.d.w2 : cur.d.w1;
  const rw2 = cur.flip ? cur.d.w1 : cur.d.w2;
  const rpf1 = cur.flip ? cur.d.pf2 : cur.d.pf1;
  const rpf2 = cur.flip ? cur.d.pf1 : cur.d.pf2;
  checked++;
  const wOk = p.w1 === rw1 && p.w2 === rw2;
  const pfOk = Math.abs(p.pf1 - rpf1) < 0.5 && Math.abs(p.pf2 - rpf2) < 0.5;
  const poOk = p.playoffs === cur.d.playoffs;
  if (!wOk || !pfOk || !poOk) {
    mism++;
    if (mism <= 12) console.log(`  ${k1}-${k2}: mine ${p.w1}-${p.w2}/${p.pf1}/${p.pf2}/po${p.playoffs}  vs report ${rw1}-${rw2}/${rpf1}/${rpf2}/po${cur.d.playoffs}`);
  }
}
console.log(`\nUnaffected pairs checked: ${checked}, mismatches: ${mism}`);

console.log('\n== David & Larson pairs (the intended correction) ==');
for (const [a, b] of [['David', 'duncan'], ['David', 'Raj'], ['David', 'Antony'], ['Larson', 'duncan'], ['Larson', 'Raj']]) {
  const [k1, k2] = [a, b].sort();
  const p = h2h[k1]?.[k2];
  const cur = getCur(a, b);
  const rw1 = cur ? (cur.flip ? cur.d.w2 : cur.d.w1) : '?';
  const rw2 = cur ? (cur.flip ? cur.d.w1 : cur.d.w2) : '?';
  console.log(`  ${k1}-${k2}: recomputed ${p ? p.w1 + '-' + p.w2 : 'none'} / seasons ${p?.seasons}  (report ${rw1}-${rw2})`);
}

// ---- Write (only with --write) ---------------------------------------------
if (WRITE) {
  for (const m of managersDoc.managers) {
    const a = allTime[m.key];
    if (!a) continue;
    m.allTime = {
      seasons: a.seasons, w: a.w, l: a.l, t: a.t,
      pf: a.pf, pa: a.pa, winPct: a.winPct,
      playoffAppearances: a.playoffAppearances, titles: a.titles,
    };
  }
  managersDoc._meta.allTimeAggregatesCaveat =
    'Recomputed from data/seasons/*.json (regular season) + champions.json by scripts/recompute.mjs. ' +
    'Playoff appearances = seasons finishing in the playoff seeds (top 6 in 2009-2010, top 4 from 2011). ' +
    'Titles from champions.json. 2010 PF/PA are rounded (standings-only source).';
  writeFileSync(resolve(root, 'data/managers.json'), JSON.stringify(managersDoc, null, 2) + '\n');

  // Manager label map for the H2H tool, built from managers.json (keeps it in
  // sync — e.g. newly-tracked managers like Irfan appear in the picker).
  const managersMap = {};
  for (const m of managersDoc.managers) {
    managersMap[m.key] = { label: m.display, since: "'" + String(m.since).slice(-2) };
  }
  const out = {
    _meta: {
      description: 'Pairwise all-time head-to-head, RECOMPUTED from data/seasons/*.json (regular + playoff games) by scripts/recompute.mjs. Directional per pair: w1/pf1/big1 = first key (alphabetical), w2/pf2/big2 = second. big1/big2 = the largest margin (points gap) in a win by that manager, with bigS1/bigS2 = the two-digit season of that game. seasons = distinct seasons the pair met. Includes playoff games.',
      source: 'data/seasons/*.json + legacy playoffs',
      generatedBy: 'scripts/recompute.mjs',
      pairs: pairCount,
    },
    managers: managersMap,
    h2h,
  };
  writeFileSync(resolve(root, 'data/h2h.json'), JSON.stringify(out, null, 2) + '\n');
  console.log('\nWROTE data/managers.json and data/h2h.json');
} else {
  console.log('\n(validate-only; re-run with --write to apply)');
}
