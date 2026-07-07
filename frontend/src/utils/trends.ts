import { nearestEvent, type ElectionEvent } from '~/data/electionEvents';
import type { ElectionYear, TrendsMetric, TrendsRow } from '~/services/googleTrends';

export type DateRange = {
  start?: string;
  end?: string;
};

export type TimelinePoint = {
  date: string;
  [key: string]: number | string | boolean | null;
};

export type Peak = {
  term: string;
  date: string;
  value: number;
  event: ElectionEvent | null;
};

export type CandidateShare = {
  term: string;
  mean: number;
  share: number;
};

export type ConcentrationLabel = 'alta' | 'moderada' | 'distribuída';

const PEAK_RATIO = 1.2;
const PARTIAL_SUFFIX = '__partial';

/** Reads the selected metric from a row (scaled may be null). */
export function metricValue(row: TrendsRow, metric: TrendsMetric): number | null {
  return metric === 'interestScaled' ? row.interestScaled : row.interestRaw;
}

export function filterByYear(rows: TrendsRow[], year: ElectionYear): TrendsRow[] {
  return rows.filter((row) => row.electionYear === year);
}

export function uniqueTerms(rows: TrendsRow[]): string[] {
  return Array.from(new Set(rows.map((row) => row.term)));
}

function meanOf(values: number[]): number {
  if (values.length === 0) {
    return 0;
  }

  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function meanInterest(rows: TrendsRow[], term: string, metric: TrendsMetric): number {
  const values: number[] = [];

  for (const row of rows) {
    if (row.term !== term) {
      continue;
    }

    const value = metricValue(row, metric);

    if (value != null) {
      values.push(value);
    }
  }

  return meanOf(values);
}

/** Candidate terms ordered by mean interest (descending). */
export function termsByMean(rows: TrendsRow[], metric: TrendsMetric): string[] {
  return uniqueTerms(rows)
    .map((term) => ({ term, mean: meanInterest(rows, term, metric) }))
    .sort((a, b) => b.mean - a.mean)
    .map((entry) => entry.term);
}

/** Top N candidate terms by mean interest — the default selection. */
export function topCandidatesByMean(rows: TrendsRow[], metric: TrendsMetric, n = 4): string[] {
  return termsByMean(rows, metric).slice(0, n);
}

/** Builds a date-indexed series for a line chart, with per-term partial flags. */
export function buildTimeline(rows: TrendsRow[], terms: string[], metric: TrendsMetric): TimelinePoint[] {
  const termSet = new Set(terms);
  const byDate = new Map<string, TimelinePoint>();

  for (const row of rows) {
    if (!termSet.has(row.term)) {
      continue;
    }

    let point = byDate.get(row.date);

    if (!point) {
      point = { date: row.date };
      byDate.set(row.date, point);
    }

    point[row.term] = metricValue(row, metric);
    point[`${row.term}${PARTIAL_SUFFIX}`] = row.isPartial;
  }

  return Array.from(byDate.values()).sort((a, b) => a.date.localeCompare(b.date));
}

/**
 * Detects peaks for a term: a value at least 20% above the previous available
 * point and above the next one. Partial (still-forming) points are ignored.
 */
export function detectPeaks(timeline: TimelinePoint[], terms: string[], year: ElectionYear): Peak[] {
  const peaks: Peak[] = [];

  for (const term of terms) {
    const points = timeline
      .map((point) => ({
        date: point.date,
        value: point[term] as number | null,
        partial: Boolean(point[`${term}${PARTIAL_SUFFIX}`]),
      }))
      .filter((point) => point.value != null) as { date: string; value: number; partial: boolean }[];

    for (let i = 1; i < points.length - 1; i += 1) {
      const current = points[i];
      const previous = points[i - 1];
      const next = points[i + 1];

      if (current.partial) {
        continue;
      }

      if (current.value > previous.value * PEAK_RATIO && current.value > next.value) {
        peaks.push({
          term,
          date: current.date,
          value: current.value,
          event: nearestEvent(current.date, year),
        });
      }
    }
  }

  return peaks;
}

/** The single highest peak across the selected terms, or null. */
export function highestPeak(peaks: Peak[]): Peak | null {
  return peaks.reduce<Peak | null>((best, peak) => (best && best.value >= peak.value ? best : peak), null);
}

export function isWithinRange(date: string, range: DateRange): boolean {
  if (range.start && date < range.start) {
    return false;
  }

  if (range.end && date > range.end) {
    return false;
  }

  return true;
}

/** Keeps only rows whose date falls within the range (an empty range keeps all). */
export function filterByRange(rows: TrendsRow[], range: DateRange): TrendsRow[] {
  return rows.filter((row) => isWithinRange(row.date, range));
}

/**
 * Share of Search for a period: each candidate's mean interest divided by the
 * sum of all candidates' mean interest. Uses mean (not sum) because the index
 * is already relative and periods may have different lengths. Partial points
 * (still-forming periods, only the latest of the `current` year) are excluded so
 * an incomplete week does not skew the period's mean.
 */
export function shareOfSearch(
  rows: TrendsRow[],
  terms: string[],
  metric: TrendsMetric,
  range: DateRange = {},
): CandidateShare[] {
  const scoped = rows.filter((row) => terms.includes(row.term) && !row.isPartial && isWithinRange(row.date, range));
  const means = terms.map((term) => ({ term, mean: meanInterest(scoped, term, metric) }));
  const total = means.reduce((sum, entry) => sum + entry.mean, 0);

  return means
    .map(({ term, mean }) => ({ term, mean, share: total > 0 ? (mean / total) * 100 : 0 }))
    .sort((a, b) => b.share - a.share);
}

/** Sum of the two largest shares. */
export function top2Concentration(shares: CandidateShare[]): number {
  return shares.slice(0, 2).reduce((sum, entry) => sum + entry.share, 0);
}

export function classifyConcentration(value: number): ConcentrationLabel {
  if (value >= 70) {
    return 'alta';
  }

  if (value >= 50) {
    return 'moderada';
  }

  return 'distribuída';
}

/** Min and max dates present in the rows. */
export function dateExtent(rows: TrendsRow[]): DateRange {
  if (rows.length === 0) {
    return {};
  }

  let min = rows[0].date;
  let max = rows[0].date;

  for (const row of rows) {
    if (row.date < min) {
      min = row.date;
    }

    if (row.date > max) {
      max = row.date;
    }
  }

  return { start: min, end: max };
}
