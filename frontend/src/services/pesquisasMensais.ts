import { fetchSheetCsv, parseCsv } from '~/services/sheets';
import type { ElectionYear } from '~/services/googleTrends';

export const POLLS_MONTHLY_TAB = 'gold_pesquisas_media_mensal_candidato';

/** Maps the integer election year of the poll table to the app's ElectionYear. */
export function electionYearFromAno(ano: string): ElectionYear {
  const normalized = ano.trim();

  return normalized === '2026' ? 'current' : (normalized as ElectionYear);
}

/**
 * One monthly-aggregated poll observation for a candidate, pooling every
 * institute (not just Datafolha) so the series has no month gaps. One row per
 * (electionYear, candidateNormalized, month).
 */
export type PollMonthlyRow = {
  date: string;
  electionYear: ElectionYear;
  monthLabel: string;
  candidateNormalized: string;
  percent: number | null;
};

/** Raw shape as it arrives from the gold spreadsheet (snake_case headers). */
type RawPollMonthlyRow = {
  ano_eleicao: string;
  data_referencia: string;
  mes_referencia: string;
  nome_candidato_normalizado: string;
  percentual_agregado: string;
};

/** Absence stays null — an aggregated percent is never coerced to zero. */
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

function mapRow(raw: RawPollMonthlyRow): PollMonthlyRow {
  return {
    date: raw.data_referencia,
    electionYear: electionYearFromAno(raw.ano_eleicao),
    monthLabel: raw.mes_referencia,
    candidateNormalized: raw.nome_candidato_normalizado,
    percent: parseNullableNumber(raw.percentual_agregado),
  };
}

/** Fetches and parses the gold monthly-aggregated (multi-institution) poll table. */
export async function fetchPollMonthlyRows(): Promise<PollMonthlyRow[]> {
  const csv = await fetchSheetCsv(POLLS_MONTHLY_TAB);
  const rows = parseCsv<RawPollMonthlyRow>(csv);

  return rows.filter((row) => row.data_referencia && row.nome_candidato_normalizado).map(mapRow);
}
