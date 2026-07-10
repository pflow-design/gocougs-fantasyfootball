// Processes the raw Yahoo lineup scrape (data/yahoo-lineups-raw.json) into the
// data the Teams feature needs, and corrects team-name labels that were mis-
// attributed in our standings (the scrape is authoritative).
//
//   node scripts/build-lineups.mjs           # compute + report, no writes
//   node scripts/build-lineups.mjs --write   # write teams-meta, static/lineups, and label fixes
//
// Team -> manager is resolved by SCORE FINGERPRINT: each scraped team is matched
// to the manager whose stored weekly scores its lineup totals reproduce. This is
// authoritative (verified against Yahoo's own manager names) and a clean bijection
// for every season.

import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const WRITE = process.argv.includes('--write');
const rj = (p) => JSON.parse(readFileSync(resolve(root, p), 'utf8'));

const raw = rj('data/yahoo-lineups-raw.json');
const managersDoc = rj('data/managers.json');
const champDoc = rj('data/champions.json');
const seasonFiles = readdirSync(resolve(root, 'data/seasons')).filter((f) => f.endsWith('.json'));
const seasons = {};
for (const f of seasonFiles) { const s = rj('data/seasons/' + f); seasons[s.year] = { file: f, s }; }
const YEARS = Object.keys(raw).map(Number).sort((a, b) => a - b);
const norm = (t) => String(t || '').replace(/\s+/g, ' ').trim();

// ---- fingerprint mapping: year -> tid -> managerKey ----
const teamNames = {};   // year -> mk -> yahoo team name (normalized)
const tidToMk = {};     // year -> tid -> mk
for (const yr of YEARS) {
  const s = seasons[yr].s;
  const stored = {};
  for (const [wk, g] of Object.entries(s.weeklyScores || {})) {
    if (!/^\d+$/.test(wk)) continue;
    for (const [a, sa, b, sb] of g) { (stored[a] ||= {})[wk] = sa; (stored[b] ||= {})[wk] = sb; }
  }
  const mgrs = Object.keys(stored);
  teamNames[yr] = {}; tidToMk[yr] = {};
  const used = {};
  for (const tid of Object.keys(raw[yr].teams)) {
    const T = raw[yr].teams[tid];
    let best = null;
    for (const mk of mgrs) {
      let d = 0, n = 0;
      for (const [wk, lu] of Object.entries(T.weeks)) if (stored[mk][wk] != null) { d += Math.abs(lu.tot - stored[mk][wk]); n++; }
      if (n > 0) { const avg = d / n; if (!best || avg < best.avg) best = { mk, avg }; }
    }
    tidToMk[yr][tid] = best.mk; teamNames[yr][best.mk] = norm(T.team); used[best.mk] = (used[best.mk] || 0) + 1;
  }
  const dup = Object.entries(used).filter(([k, v]) => v > 1);
  if (dup.length) console.log(`WARN ${yr} fingerprint collision: ${dup.map(([k, v]) => k + 'x' + v).join(',')}`);
}

// ---- managers meta (subset) ----
const managers = managersDoc.managers.map((m) => ({
  key: m.key, name: m.display, since: m.since, status: m.status, currentTeam: m.currentTeam,
  allTime: m.allTime, playoff: m.playoff || null,
}));

// ---- seasons per manager ----
const seasonsByMgr = {};
for (const yr of YEARS) for (const st of seasons[yr].s.standings) if (st.managerKey) (seasonsByMgr[st.managerKey] ||= []).push(yr);

// ---- lineups per season (keyed by mk) + full lineup lookup for wk resolution ----
const lineupsByYear = {}; // year -> mk -> weeks
for (const yr of YEARS) {
  lineupsByYear[yr] = {};
  for (const tid of Object.keys(raw[yr].teams)) lineupsByYear[yr][tidToMk[yr][tid]] = raw[yr].teams[tid].weeks;
}
const findWk = (yr, mk, score) => {
  const wks = lineupsByYear[yr]?.[mk] || {};
  let best = null;
  for (const [wk, lu] of Object.entries(wks)) { const d = Math.abs(lu.tot - score); if (best === null || d < best.d) best = { wk: Number(wk), d }; }
  return best && best.d < 0.5 ? best.wk : null;
};

// ---- schedules: year -> mk -> [ {wk, opp, pf, pa, res, playoff, label} ] ----
const schedules = {};
for (const yr of YEARS) {
  schedules[yr] = {};
  const add = (mk, row) => (schedules[yr][mk] ||= []).push(row);
  for (const [wk, games] of Object.entries(seasons[yr].s.weeklyScores || {})) {
    if (!/^\d+$/.test(wk)) continue;
    for (const [a, sa, b, sb] of games) {
      add(a, { wk: +wk, opp: b, pf: sa, pa: sb, res: sa > sb ? 'W' : sa < sb ? 'L' : 'T', playoff: false });
      add(b, { wk: +wk, opp: a, pf: sb, pa: sa, res: sb > sa ? 'W' : sb < sa ? 'L' : 'T', playoff: false });
    }
  }
  const revName = {}; for (const mk in teamNames[yr]) revName[teamNames[yr][mk]] = mk;
  for (const [gname, grp] of Object.entries(seasons[yr].s.playoffs || {})) {
    for (const g of grp.games || []) {
      const wmk = revName[norm(g.winner.team)], lmk = revName[norm(g.loser.team)];
      if (!wmk || !lmk) continue;
      const label = g.label || (gname === 'championship' ? 'Championship' : 'Semifinal');
      const wk = findWk(yr, wmk, g.winner.score) ?? findWk(yr, lmk, g.loser.score);
      add(wmk, { wk, opp: lmk, pf: g.winner.score, pa: g.loser.score, res: 'W', playoff: true, label });
      add(lmk, { wk, opp: wmk, pf: g.loser.score, pa: g.winner.score, res: 'L', playoff: true, label });
    }
  }
  for (const mk in schedules[yr]) schedules[yr][mk].sort((x, y) => (x.playoff - y.playoff) || ((x.wk ?? 99) - (y.wk ?? 99)));
}

const meta = { years: YEARS, managers, teamNames, seasonsByMgr, schedules };

// ---- team-name label corrections (standings + champions) ----
const fixes = [];
for (const yr of YEARS) {
  for (const st of seasons[yr].s.standings) {
    const correct = teamNames[yr][st.managerKey];
    if (correct && norm(st.team) !== correct) { fixes.push({ yr, mk: st.managerKey, from: st.team, to: correct }); st.team = correct; }
  }
}
const champFixes = [];
for (const c of champDoc.byYear || []) {
  const correct = teamNames[c.year]?.[c.champion];
  if (correct && c.team && norm(c.team) !== correct) { champFixes.push({ yr: c.year, from: c.team, to: correct }); c.team = correct; }
}

// ---- report ----
console.log(`Seasons ${YEARS.length}, managers ${managers.length}`);
console.log(`Team-name label fixes (standings): ${fixes.length}`);
for (const f of fixes) console.log(`  ${f.yr} ${f.mk}: "${f.from}" -> "${f.to}"`);
console.log(`Champion team-name fixes: ${champFixes.length}`);
for (const f of champFixes) console.log(`  ${f.yr}: "${f.from}" -> "${f.to}"`);

if (WRITE) {
  writeFileSync(resolve(root, 'data/teams-meta.json'), JSON.stringify(meta));
  for (const yr of YEARS) writeFileSync(resolve(root, `static/lineups/${yr}.json`), JSON.stringify(lineupsByYear[yr]));
  // Only rewrite season files that actually changed (these are standard-formatted;
  // 2025.json/champions.json use compact formatting and are corrected by hand).
  const changed = [...new Set(fixes.map((f) => f.yr))].sort();
  for (const yr of changed) writeFileSync(resolve(root, 'data/seasons/' + seasons[yr].file), JSON.stringify(seasons[yr].s, null, 2) + '\n');
  console.log(`\nWROTE data/teams-meta.json, static/lineups/*.json, and corrected season files: ${changed.join(', ')}`);
  if (champFixes.length) console.log(`APPLY BY HAND (champions.json is compact-formatted): ${champFixes.map((f) => f.yr + ' "' + f.from + '" -> "' + f.to + '"').join('; ')}`);
} else {
  console.log('\n(dry run — pass --write to save)');
}
