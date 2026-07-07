import type { ElectionYear } from '~/services/googleTrends';
import type { TrendsMonthlyRow } from '~/services/googleTrendsMonthly';
import type { PollMonthlyRow } from '~/services/pesquisasMensais';
import { candidatesMatchForElection } from '~/utils/candidateNormalization';
import { isWithinRange, type DateRange } from '~/utils/trends';

/** One month of the crossed series: attention index and poll percentage. */
export type AttentionVsPollingPoint = {
  date: string;
  ts: number;
  attention: number | null;
  polling: number | null;
};

type Bucket = {
  attention: number | null;
  polling: number | null;
};

function bucketFor(byDate: Map<string, Bucket>, date: string): Bucket {
  let bucket = byDate.get(date);

  if (!bucket) {
    bucket = { attention: null, polling: null };
    byDate.set(date, bucket);
  }

  return bucket;
}

export function filterTrendsMonthlyByYear(rows: TrendsMonthlyRow[], year: ElectionYear): TrendsMonthlyRow[] {
  return rows.filter((row) => row.electionYear === year);
}

/** Trends terms ordered by mean monthly interest (descending) — candidate options for this chart's filter. */
export function trendsTermsByMeanMonthly(rows: TrendsMonthlyRow[]): string[] {
  const totals = new Map<string, { sum: number; count: number }>();

  for (const row of rows) {
    if (row.interestMean == null) {
      continue;
    }

    const entry = totals.get(row.term) ?? { sum: 0, count: 0 };
    entry.sum += row.interestMean;
    entry.count += 1;
    totals.set(row.term, entry);
  }

  return Array.from(totals.entries())
    .map(([term, { sum, count }]) => ({ term, mean: count > 0 ? sum / count : 0 }))
    .sort((a, b) => b.mean - a.mean)
    .map((entry) => entry.term);
}

/**
 * Crosses public attention (Google Trends) with poll percentage for a single
 * candidate, month by month. Both inputs are already month-aggregated gold
 * tables (`proc_google_trends_all_elections_interest_monthly` and
 * `gold_pesquisas_media_mensal_candidato`), so this only needs to join them by
 * (candidate, month) — no further averaging.
 *
 * - Attention: `interestMean` of the Trends term matching `candidate`,
 *   **clipped to the month span covered by that candidate's polls** so the
 *   chart never stretches the Trends line over months where no poll exists.
 *   When the candidate has no poll in scope, the window falls back to the
 *   full range and only the attention line is shown.
 *
 * Missing sides stay `null` (never 0 or interpolated), and the result is
 * sorted ascending by month so the time axis stays continuous.
 */
export function buildAttentionVsPollingMonthlySeries(
  trendsMonthlyRows: TrendsMonthlyRow[],
  pollMonthlyRows: PollMonthlyRow[],
  candidate: string,
  year: ElectionYear,
  range: DateRange = {},
): AttentionVsPollingPoint[] {
  const byDate = new Map<string, Bucket>();

  for (const row of pollMonthlyRows) {
    if (row.electionYear !== year || row.percent == null) {
      continue;
    }

    if (!candidatesMatchForElection(row.candidateNormalized, candidate, year)) {
      continue;
    }

    if (!isWithinRange(row.date, range)) {
      continue;
    }

    bucketFor(byDate, row.date).polling = row.percent;
  }

  // The poll months are the temporal base: the Trends line is clipped to
  // their span so both series cover the exact same period. With no polls in
  // scope, the whole range stays open (attention-only view).
  const pollDates = Array.from(byDate.keys()).sort();
  const pollWindow: DateRange =
    pollDates.length > 0 ? { start: pollDates[0], end: pollDates[pollDates.length - 1] } : range;

  for (const row of trendsMonthlyRows) {
    if (row.electionYear !== year || row.term !== candidate || row.interestMean == null) {
      continue;
    }

    if (!isWithinRange(row.date, range) || !isWithinRange(row.date, pollWindow)) {
      continue;
    }

    bucketFor(byDate, row.date).attention = row.interestMean;
  }

  return Array.from(byDate.entries())
    .map(([date, bucket]) => ({
      date,
      ts: Date.parse(date),
      attention: bucket.attention,
      polling: bucket.polling,
    }))
    .sort((a, b) => a.date.localeCompare(b.date));
}
