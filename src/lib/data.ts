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

// Honest champion resolution: `known` is true only when the season actually
// records a champion. Otherwise we fall back to the regular-season #1 seed, and
// callers must NOT present it as the title winner (champions for 2012-2022 are
// still pending extraction — see champions.json).
export function championInfo(season: Season): { known: boolean; team?: string; key: string | null } {
  const c: any = (season as any).champion;
  const top = season.standings.find((s) => s.rank === 1);
  if (c && (c.managerKey || c.manager)) {
    return { known: true, team: c.team ?? top?.team, key: c.managerKey ?? c.manager ?? null };
  }
  return { known: false, team: top?.team, key: top?.managerKey ?? null };
}

export { managers, records, champions, h2h };
