// Extracts the canonical h2hData + MANAGERS map from reference/kdp_report.html
// and writes data/h2h.json. The report's embedded h2hData is the authoritative
// version (canonical keys KyleK/KyleP/Rudee/Larson/Bradley + label map), and
// supersedes the older legacy/h2h_all.js.
//
// Run once Node 22+ is installed:  node scripts/extract-h2h.mjs
//
// Pair objects are directional: for pair A -> B, w1/pf1/big1 belong to A and
// w2/pf2/big2 to B. `last` is the most recent meeting. `playoffs` = count of
// playoff meetings, `seasons` = seasons the two overlapped. The report stores
// each unordered pair once; the site's getH2H() flips the record for reverse
// lookups (see reference/kdp_report.html).

import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const html = readFileSync(resolve(root, 'reference/kdp_report.html'), 'utf8');

// Grab a `var NAME = { ... };` object literal by brace-matching from the `{`.
function extractObjectLiteral(src, varName) {
  const start = src.indexOf('var ' + varName);
  if (start === -1) throw new Error('Could not find var ' + varName);
  const open = src.indexOf('{', start);
  let depth = 0;
  for (let i = open; i < src.length; i++) {
    const c = src[i];
    if (c === '{') depth++;
    else if (c === '}') {
      depth--;
      if (depth === 0) return src.slice(open, i + 1);
    }
  }
  throw new Error('Unbalanced braces for ' + varName);
}

// The report file is trusted (authored in-repo), so evaluating its object
// literals is safe and exact — no fragile hand-transcription of ~78 pairs.
const evalObj = (literal) => new Function('return (' + literal + ')')();

const h2hData = evalObj(extractObjectLiteral(html, 'h2hData'));
const managers = evalObj(extractObjectLiteral(html, 'MANAGERS'));

const pairCount = Object.values(h2hData).reduce((n, o) => n + Object.keys(o).length, 0);

const out = {
  _meta: {
    description:
      'Pairwise all-time head-to-head aggregates (NOT weekly). Extracted from ' +
      "reference/kdp_report.html's embedded h2hData by scripts/extract-h2h.mjs. " +
      'Directional per unordered pair: w1/pf1/big1 = first key, w2/pf2/big2 = second key. ' +
      'Aggregates likely include playoff games (unlike the regular-season-only records).',
    source: 'reference/kdp_report.html',
    generatedBy: 'scripts/extract-h2h.mjs',
    pairs: pairCount,
  },
  managers, // key -> { label, since }
  h2h: h2hData,
};

mkdirSync(resolve(root, 'data'), { recursive: true });
writeFileSync(resolve(root, 'data/h2h.json'), JSON.stringify(out, null, 2) + '\n');
console.log(`Wrote data/h2h.json — ${pairCount} pairs, ${Object.keys(managers).length} managers.`);
