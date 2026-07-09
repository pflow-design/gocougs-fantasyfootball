// Central data access for the site build. All JSON lives in /data (versioned,
// the single source of truth). Season files are loaded eagerly and sorted
// newest-first. See data/SCHEMA.md for shapes.

import managers from '../../data/managers.json';
import records from '../../data/records.json';
import champions from '../../data/champions.json';
import h2h from '../../data/h2h.json';

const seasonModules = import.meta.glob('../../data/seasons/*.json', { eager: true });

export interface SeasonStanding {
  rank: number;
  team?: string;
  manager: string | null;
  managerKey: string | null;
  w: number;
  l: number;
  t?: number;
  pf: number;
  pa?: number;
  diff?: number;
  streak?: string;
  [k: string]: unknown;
}
export interface Season {
  year: number;
  leagueId?: string;
  yahooUrl?: string;
  teams: number;
  regularSeasonWeeks?: number;
  champion?: { managerKey?: string; team?: string } | null;
  standings: SeasonStanding[];
  weeklyScores?: Record<string, Array<[string, number, string, number]>>;
  [k: string]: unknown;
}

export const seasons: Season[] = Object.values(seasonModules)
  .map((m: any) => m.default as Season)
  .sort((a, b) => b.year - a.year);

export const seasonByYear = (year: number): Season | undefined =>
  seasons.find((s) => s.year === year);

// Champion resolution, sourced from champions.json (the authoritative list of
// title winners + their teams). Falls back to the season file's champion, then
// to the regular-season #1 seed — in which case `known` is false and callers
// must NOT present it as the title winner. `team` may be undefined when the
// champion's team name isn't known for that year.
const champByYear = new Map<number, any>(
  ((champions as any).byYear as any[]).map((c) => [c.year, c])
);
export function championInfo(season: Season): { known: boolean; team?: string; key: string | null } {
  const top = season.standings.find((s) => s.rank === 1);
  const cy = champByYear.get(season.year);
  if (cy && cy.champion) {
    return { known: true, team: cy.team ?? undefined, key: cy.champion };
  }
  const sc: any = (season as any).champion;
  if (sc && (sc.managerKey || sc.manager)) {
    return { known: true, team: sc.team ?? top?.team, key: sc.managerKey ?? sc.manager ?? null };
  }
  return { known: false, team: top?.team, key: top?.managerKey ?? null };
}

export { managers, records, champions, h2h };
