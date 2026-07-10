// One-off correction: the enrich step under-captured the 2016 and 2019 playoff
// brackets (each stored only 1 semifinal + the championship game). This restores
// the full championship bracket (both semifinals + championship + 3rd-place game)
// from the legacy PLAYOFFS data, with the corrected team names.
//
//   node scripts/fix-playoffs.mjs --write
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const WRITE = process.argv.includes('--write');

const fixes = {
  2016: {
    semifinals: { week: 15, games: [
      { label: 'Semifinal 1', winner: { team: 'Russell and Flow', score: 93.56 }, loser: { team: 'shmoney maker', score: 89.49 } },
      { label: 'Semifinal 2', winner: { team: 'Swing Your Sword', score: 144.07 }, loser: { team: 'Russell Sprouts', score: 78.50 } },
    ] },
    championship: { week: 16, games: [
      { label: 'Championship Game', winner: { team: 'Russell and Flow', score: 140.54 }, loser: { team: 'Swing Your Sword', score: 89.51 } },
      { label: '3rd Place Game', winner: { team: 'shmoney maker', score: 143.61 }, loser: { team: 'Russell Sprouts', score: 121.73 } },
    ] },
  },
  2019: {
    semifinals: { week: 15, games: [
      { label: 'Semifinal 1', winner: { team: 'WokeUpFeelinDangerus', score: 151.77 }, loser: { team: 'My Ball Zach Ertz', score: 91.28 } },
      { label: 'Semifinal 2', winner: { team: 'Candyman', score: 163.82 }, loser: { team: 'shmoney maker', score: 134.51 } },
    ] },
    championship: { week: 16, games: [
      { label: 'Championship Game', winner: { team: 'Candyman', score: 164.05 }, loser: { team: 'WokeUpFeelinDangerus', score: 103.21 } },
      { label: '3rd Place Game', winner: { team: 'My Ball Zach Ertz', score: 105.00 }, loser: { team: 'shmoney maker', score: 101.40 } },
    ] },
  },
};

for (const [yr, playoffs] of Object.entries(fixes)) {
  const p = resolve(root, `data/seasons/${yr}.json`);
  const s = JSON.parse(readFileSync(p, 'utf8'));
  const before = (s.playoffs?.semifinals?.games?.length || 0) + (s.playoffs?.championship?.games?.length || 0);
  s.playoffs = playoffs;
  const after = playoffs.semifinals.games.length + playoffs.championship.games.length;
  console.log(`${yr}: playoff games ${before} -> ${after}`);
  if (WRITE) writeFileSync(p, JSON.stringify(s, null, 2) + '\n');
}
console.log(WRITE ? '\nWROTE 2016.json, 2019.json' : '\n(dry run — pass --write)');
