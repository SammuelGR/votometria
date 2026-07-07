import type { ElectionYear, TrendsRow } from '~/services/googleTrends';
import type { PollMonthlyRow } from '~/services/pesquisasMensais';
import type { WeeklyMarketExpectationPoint } from '~/fetchers/marketExpectations';
import { candidatesMatchForElection } from '~/utils/candidateNormalization';
import { isWithinRange, type DateRange } from '~/utils/trends';

const DAY_IN_MS = 24 * 60 * 60 * 1000;

/** One date of the crossed series: attention index (weekly) and poll percentage (monthly). */
export type ElectoralPanoramaPoint = {
  date: string;
  ts: number;
  attention: number | null;
  polling: number | null;
  marketExpectation: number | null;
};

type Bucket = {
  referenceDate: string;
  attention: number | null;
  marketExpectation: number | null;
};

type PollObservation = {
  date: string;
  percent: number;
};

function bucketFor(byDate: Map<string, Bucket>, date: string, referenceDate: string): Bucket {
  let bucket = byDate.get(date);

  if (!bucket) {
    bucket = { referenceDate, attention: null, marketExpectation: null };
    byDate.set(date, bucket);
  }

  if (referenceDate > bucket.referenceDate) {
    bucket.referenceDate = referenceDate;
  }

  return bucket;
}

function dateFromTimestamp(timestamp: number): string {
  return new Date(timestamp).toISOString().slice(0, 10);
}

function startOfUtcWeek(date: string): string {
  const timestamp = Date.parse(date);
  const day = new Date(timestamp).getUTCDay();
  const daysSinceMonday = day === 0 ? 6 : day - 1;

  return dateFromTimestamp(timestamp - daysSinceMonday * DAY_IN_MS);
}

function latestPollingAtOrBefore(pollObservations: PollObservation[], date: string): number | null {
  let latest: number | null = null;

  for (const observation of pollObservations) {
    if (observation.date > date) {
      break;
    }

    latest = observation.percent;
  }

  return latest;
}

/**
 * Crosses public attention (Google Trends) with poll percentage for a single
 * candidate. Attention comes from the Trends long table
 * (`proc_google_trends_all_elections_interest_long`, `interest_raw`, one row
 * per collection date — weekly cadence, not aligned to month boundaries)
 * while polling comes from the month-aggregated gold table
 * (`gold_pesquisas_media_mensal_candidato`, one row per month's first day)
 * and market expectations come from weekly Polymarket closing points.
 * Attention and market expectation values are placed on a shared UTC week
 * bucket without changing their values. Polling is carried forward into those
 * same weekly buckets using the latest stored monthly value.
 *
 * - Attention: `interestRaw` of the Trends term matching `candidate`,
 *   **clipped to the date span covered by that candidate's polls** so the
 *   chart never stretches the Trends line over months where no poll exists.
 *   When the candidate has no poll in scope, the window falls back to the
 *   full range and only the attention line is shown.
 *
 * Missing sides stay `null` (never 0 or interpolated), and the result is sorted
 * ascending by date so the time axis stays continuous.
 */
export function buildElectoralPanoramaSeries(
  trendsRows: TrendsRow[],
  pollMonthlyRows: PollMonthlyRow[],
  candidate: string,
  year: ElectionYear,
  range: DateRange = {},
  weeklyMarketExpectationRows: WeeklyMarketExpectationPoint[] = [],
): ElectoralPanoramaPoint[] {
  const byDate = new Map<string, Bucket>();
  const pollObservations: PollObservation[] = [];

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

    pollObservations.push({ date: row.date, percent: row.percent });
  }

  pollObservations.sort((a, b) => a.date.localeCompare(b.date));

  // The poll months are the temporal base: the Trends line is clipped to
  // their span so both series cover the exact same period. With no polls in
  // scope, the whole range stays open (attention-only view).
  const pollDates = pollObservations.map((observation) => observation.date).sort();
  const pollWindow: DateRange =
    pollDates.length > 0 ? { start: pollDates[0], end: pollDates[pollDates.length - 1] } : range;

  for (const row of trendsRows) {
    if (row.electionYear !== year || row.term !== candidate) {
      continue;
    }

    if (!isWithinRange(row.date, range) || !isWithinRange(row.date, pollWindow)) {
      continue;
    }

    bucketFor(byDate, startOfUtcWeek(row.date), row.date).attention = row.interestRaw;
  }

  for (const row of weeklyMarketExpectationRows) {
    if (!isWithinRange(row.date, range)) {
      continue;
    }

    bucketFor(byDate, startOfUtcWeek(row.date), row.date).marketExpectation = row.probability;
  }

  return Array.from(byDate.entries())
    .map(([date, bucket]) => ({
      date,
      ts: Date.parse(date),
      attention: bucket.attention,
      polling: latestPollingAtOrBefore(pollObservations, bucket.referenceDate),
      marketExpectation: bucket.marketExpectation,
    }))
    .sort((a, b) => a.date.localeCompare(b.date));
}
