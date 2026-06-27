import { fetchSheetCsv, parseCsv } from '~/services/sheets';

export const TRENDS_TAB = 'proc_google_trends_all_elections_interest_long';

export type ElectionYear = '2018' | '2022' | 'current';

export type TrendsMetric = 'interestRaw' | 'interestScaled';

/** One processed Google Trends observation (long format). */
export type TrendsRow = {
  date: string;
  electionYear: ElectionYear;
  term: string;
  interestRaw: number;
  interestScaled: number | null;
  geo: string;
  timeframe: string;
  source: string;
  batchId: string;
  anchorTerm: string;
  isAnchor: boolean;
  isPartial: boolean;
  collectedAt: string;
};

/** Raw shape as it arrives from the spreadsheet (snake_case headers). */
type RawTrendsRow = {
  date: string;
  election_year: string;
  term: string;
  interest_raw: string;
  interest_scaled: string;
  geo: string;
  timeframe: string;
  source: string;
  batch_id: string;
  anchor_term: string;
  is_anchor: string;
  is_partial: string;
  collected_at: string;
};

function parseNumber(value: string | undefined): number {
  const parsed = Number(value);

  return Number.isFinite(parsed) ? parsed : 0;
}

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

function parseBoolean(value: string | undefined): boolean {
  return (value ?? '').trim().toLowerCase() === 'true';
}

function mapRow(raw: RawTrendsRow): TrendsRow {
  return {
    date: raw.date,
    electionYear: raw.election_year as ElectionYear,
    term: raw.term,
    interestRaw: parseNumber(raw.interest_raw),
    interestScaled: parseNullableNumber(raw.interest_scaled),
    geo: raw.geo,
    timeframe: raw.timeframe,
    source: raw.source,
    batchId: raw.batch_id,
    anchorTerm: raw.anchor_term,
    isAnchor: parseBoolean(raw.is_anchor),
    isPartial: parseBoolean(raw.is_partial),
    collectedAt: raw.collected_at,
  };
}

/** Fetches and parses the consolidated Google Trends long table. */
export async function fetchTrendsRows(): Promise<TrendsRow[]> {
  const csv = await fetchSheetCsv(TRENDS_TAB);
  const rows = parseCsv<RawTrendsRow>(csv);

  return rows.filter((row) => row.date && row.term).map(mapRow);
}
