import type { ElectionYear, TrendsRow } from '~/services/googleTrends';
import type { PollMonthlyRow } from '~/services/pesquisasMensais';
import type { WeeklyMarketExpectationPoint } from '~/fetchers/marketExpectations';
import { candidatesMatchForElection } from '~/utils/candidateNormalization';
import type { DateRange } from '~/utils/trends';

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

function displayStartForRange(range: DateRange): string | null {
  return range.start ? startOfUtcWeek(range.start) : null;
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
 * The selected window only defines the first displayed week. Source
 * observations are kept available to seed carried-forward values and to show
 * all subsequent public-attention points.
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

    pollObservations.push({ date: row.date, percent: row.percent });
  }

  pollObservations.sort((a, b) => a.date.localeCompare(b.date));

  for (const row of trendsRows) {
    if (row.electionYear !== year || row.term !== candidate) {
      continue;
    }

    bucketFor(byDate, startOfUtcWeek(row.date), row.date).attention = row.interestRaw;
  }

  for (const row of weeklyMarketExpectationRows) {
    bucketFor(byDate, startOfUtcWeek(row.date), row.date).marketExpectation = row.probability;
  }

  const displayStart = displayStartForRange(range);

  return Array.from(byDate.entries())
    .filter(([date]) => !displayStart || date >= displayStart)
    .map(([date, bucket]) => ({
      date,
      ts: Date.parse(date),
      attention: bucket.attention,
      polling: latestPollingAtOrBefore(pollObservations, bucket.referenceDate),
      marketExpectation: bucket.marketExpectation,
    }))
    .sort((a, b) => a.date.localeCompare(b.date));
}
