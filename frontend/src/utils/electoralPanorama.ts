import type { ElectionYear, TrendsRow } from '~/services/googleTrends';
import type { PollMonthlyRow } from '~/services/pesquisasMensais';
import type { MonthlyMarketExpectationPoint } from '~/fetchers/marketExpectations';
import { candidatesMatchForElection } from '~/utils/candidateNormalization';
import { isWithinRange, type DateRange } from '~/utils/trends';

/** One date of the crossed series: attention index (weekly) and poll percentage (monthly). */
export type ElectoralPanoramaPoint = {
  date: string;
  ts: number;
  attention: number | null;
  polling: number | null;
  marketExpectation: number | null;
};

type Bucket = {
  attention: number | null;
  polling: number | null;
  marketExpectation: number | null;
};

function bucketFor(byDate: Map<string, Bucket>, date: string): Bucket {
  let bucket = byDate.get(date);

  if (!bucket) {
    bucket = { attention: null, polling: null, marketExpectation: null };
    byDate.set(date, bucket);
  }

  return bucket;
}

/**
 * Crosses public attention (Google Trends) with poll percentage for a single
 * candidate. Attention comes from the Trends long table
 * (`proc_google_trends_all_elections_interest_long`, `interest_raw`, one row
 * per collection date — weekly cadence, not aligned to month boundaries)
 * while polling comes from the month-aggregated gold table
 * (`gold_pesquisas_media_mensal_candidato`, one row per month's first day).
 * The two are merged by exact date into the same series, so most months a
 * poll point sits on its own date alongside — not on top of — the nearest
 * attention points; each keeps its own line on the chart's shared time axis.
 *
 * - Attention: `interestRaw` of the Trends term matching `candidate`,
 *   **clipped to the date span covered by that candidate's polls** so the
 *   chart never stretches the Trends line over months where no poll exists.
 *   When the candidate has no poll in scope, the window falls back to the
 *   full range and only the attention line is shown.
 *
 * Missing sides stay `null` (never 0 or interpolated), and the result is
 * sorted ascending by date so the time axis stays continuous.
 */
export function buildElectoralPanoramaSeries(
  trendsRows: TrendsRow[],
  pollMonthlyRows: PollMonthlyRow[],
  candidate: string,
  year: ElectionYear,
  range: DateRange = {},
  monthlyMarketExpectationRows: MonthlyMarketExpectationPoint[] = [],
): ElectoralPanoramaPoint[] {
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

  for (const row of trendsRows) {
    if (row.electionYear !== year || row.term !== candidate) {
      continue;
    }

    if (!isWithinRange(row.date, range) || !isWithinRange(row.date, pollWindow)) {
      continue;
    }

    bucketFor(byDate, row.date).attention = row.interestRaw;
  }

  for (const row of monthlyMarketExpectationRows) {
    if (!isWithinRange(row.date, range)) {
      continue;
    }

    bucketFor(byDate, row.date).marketExpectation = row.probability;
  }

  return Array.from(byDate.entries())
    .map(([date, bucket]) => ({
      date,
      ts: Date.parse(date),
      attention: bucket.attention,
      polling: bucket.polling,
      marketExpectation: bucket.marketExpectation,
    }))
    .sort((a, b) => a.date.localeCompare(b.date));
}
