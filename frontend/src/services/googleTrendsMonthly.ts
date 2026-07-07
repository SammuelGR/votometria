import { fetchSheetCsv, parseCsv } from '~/services/sheets';
import type { ElectionYear } from '~/services/googleTrends';

export const TRENDS_MONTHLY_TAB = 'proc_google_trends_all_elections_interest_monthly';

/**
 * One month-aggregated Google Trends observation: mean of `interest_raw`
 * within the month for a single term. Dedicated to crossing with other
 * month-granularity sources (e.g. electoral polls) without daily noise.
 */
export type TrendsMonthlyRow = {
  date: string;
  electionYear: ElectionYear;
  term: string;
  interestMean: number | null;
};

/** Raw shape as it arrives from the gold spreadsheet (snake_case headers). */
type RawTrendsMonthlyRow = {
  election_year: string;
  date: string;
  term: string;
  interest_mean: string;
};

/** Absence stays null — a mean interest is never coerced to zero. */
function parseNullableNumber(value: string | undefined): number | null {
  if (value == null) {
    return null;
  }

  const normalized = value.trim().toLowerCase();

  if (normalized === '' || normalized === 'nan' || normalized === 'none') {
    return null;
  }

  const parsed = Number(normalized);

  return Number.isFinite(parsed) ? parsed : null;
}

function mapRow(raw: RawTrendsMonthlyRow): TrendsMonthlyRow {
  return {
    date: raw.date,
    electionYear: raw.election_year as ElectionYear,
    term: raw.term,
    interestMean: parseNullableNumber(raw.interest_mean),
  };
}

/** Fetches and parses the month-aggregated Google Trends gold table. */
export async function fetchTrendsMonthlyRows(): Promise<TrendsMonthlyRow[]> {
  const csv = await fetchSheetCsv(TRENDS_MONTHLY_TAB);
  const rows = parseCsv<RawTrendsMonthlyRow>(csv);

  return rows.filter((row) => row.date && row.term).map(mapRow);
}
