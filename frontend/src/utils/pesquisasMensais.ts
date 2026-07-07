import type { ElectionYear } from '~/services/googleTrends';
import type { PollMonthlyRow } from '~/services/pesquisasMensais';

export type PollMonthlyPoint = {
  date: string;
  mesReferencia: string;
  [candidate: string]: number | string | null;
};

export function filterPollMonthlyByYear(rows: PollMonthlyRow[], year: ElectionYear): PollMonthlyRow[] {
  return rows.filter((row) => row.electionYear === year);
}

function uniqueCandidates(rows: PollMonthlyRow[]): string[] {
  return Array.from(new Set(rows.map((row) => row.candidateNormalized)));
}

function meanPercent(rows: PollMonthlyRow[], candidate: string): number {
  const values: number[] = [];

  for (const row of rows) {
    if (row.candidateNormalized !== candidate || row.percent == null) {
      continue;
    }

    values.push(row.percent);
  }

  if (values.length === 0) {
    return 0;
  }

  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

/** Candidates ordered by mean aggregated percent (descending). */
export function candidatesByMean(rows: PollMonthlyRow[]): string[] {
  return uniqueCandidates(rows)
    .map((candidate) => ({ candidate, mean: meanPercent(rows, candidate) }))
    .sort((a, b) => b.mean - a.mean)
    .map((entry) => entry.candidate);
}

/** Top N candidates by mean aggregated percent — the default selection. */
export function topPollCandidatesByMean(rows: PollMonthlyRow[], n = 4): string[] {
  return candidatesByMean(rows).slice(0, n);
}

/**
 * Builds a date-indexed monthly series for the line chart: one point per
 * month, one key per selected candidate. A candidate absent from a given
 * month simply has no key on that point — never filled with 0 or
 * interpolated, so the chart line has a real gap there.
 */
export function buildPollMonthlyTimeline(rows: PollMonthlyRow[], candidates: string[]): PollMonthlyPoint[] {
  const candidateSet = new Set(candidates);
  const byDate = new Map<string, PollMonthlyPoint>();

  for (const row of rows) {
    if (!candidateSet.has(row.candidateNormalized) || row.percent == null) {
      continue;
    }

    let point = byDate.get(row.date);

    if (!point) {
      point = { date: row.date, mesReferencia: row.monthLabel };
      byDate.set(row.date, point);
    }

    point[row.candidateNormalized] = row.percent;
  }

  return Array.from(byDate.values()).sort((a, b) => a.date.localeCompare(b.date));
}

/** Presentable label for a normalized candidate key (the only name the gold table exposes). */
export function formatCandidateLabel(candidateNormalized: string): string {
  return candidateNormalized
    .split(' ')
    .filter(Boolean)
    .map((word) => word[0].toUpperCase() + word.slice(1))
    .join(' ');
}
