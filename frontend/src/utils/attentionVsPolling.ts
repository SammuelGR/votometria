import type { ElectionYear, TrendsMetric, TrendsRow } from '~/services/googleTrends';
import type { PollRow } from '~/services/pesquisas';
import { candidatesMatchForElection } from '~/utils/candidateNormalization';
import { isWithinRange, metricValue, type DateRange } from '~/utils/trends';

/** One day of the crossed series: attention index and poll percentage. */
export type AttentionVsPollingPoint = {
  date: string;
  ts: number;
  attention: number | null;
  polling: number | null;
};

type Bucket = {
  attention: number | null;
  pollingValues: number[];
};

function bucketFor(byDate: Map<string, Bucket>, date: string): Bucket {
  let bucket = byDate.get(date);

  if (!bucket) {
    bucket = { attention: null, pollingValues: [] };
    byDate.set(date, bucket);
  }

  return bucket;
}

function mean(values: number[]): number {
  return values.reduce((sum, value) => sum + value, 0) / values.length;
}

/**
 * Crosses public attention (Google Trends) with poll percentage for a single
 * candidate over a shared time window.
 *
 * - Polling: the mean of `percentual_numero` across every poll of the equivalent
 *   candidate on that date (multiple institutes/scenarios collapse to a daily
 *   mean, matching the Python `build_gold` aggregation).
 * - Attention: the Trends value of `candidate`'s term, **clipped to the date span
 *   covered by that candidate's polls**. The poll dataset is the temporal base:
 *   both series share the same [first poll, last poll] window so the chart never
 *   stretches the Trends line over months where no poll exists. When the
 *   candidate has no poll in scope, the window falls back to the full range and
 *   only the attention line is shown.
 *
 * Missing sides stay `null` (never 0), nothing is interpolated or rescaled, and
 * the result is sorted ascending by date so the time axis stays continuous.
 */
export function buildAttentionVsPollingSeries(
  trendsRows: TrendsRow[],
  pollRows: PollRow[],
  candidate: string,
  year: ElectionYear,
  metric: TrendsMetric,
  range: DateRange = {},
): AttentionVsPollingPoint[] {
  const byDate = new Map<string, Bucket>();

  for (const row of pollRows) {
    if (row.electionYear !== year || row.percent == null) {
      continue;
    }

    if (!candidatesMatchForElection(row.candidate, candidate, year)) {
      continue;
    }

    if (!isWithinRange(row.date, range)) {
      continue;
    }

    bucketFor(byDate, row.date).pollingValues.push(row.percent);
  }

  // The poll dates are the temporal base: the Trends line is clipped to their
  // span so both series cover the exact same period. With no polls in scope, the
  // whole range stays open (attention-only view).
  const pollDates = Array.from(byDate.keys()).sort();
  const pollWindow: DateRange =
    pollDates.length > 0 ? { start: pollDates[0], end: pollDates[pollDates.length - 1] } : range;

  for (const row of trendsRows) {
    if (row.electionYear !== year || row.term !== candidate) {
      continue;
    }

    if (!isWithinRange(row.date, range) || !isWithinRange(row.date, pollWindow)) {
      continue;
    }

    bucketFor(byDate, row.date).attention = metricValue(row, metric);
  }

  return Array.from(byDate.entries())
    .map(([date, bucket]) => ({
      date,
      ts: Date.parse(date),
      attention: bucket.attention,
      polling: bucket.pollingValues.length > 0 ? mean(bucket.pollingValues) : null,
    }))
    .sort((a, b) => a.date.localeCompare(b.date));
}
