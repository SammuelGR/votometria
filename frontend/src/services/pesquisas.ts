import { fetchSheetCsv, parseCsv } from '~/services/sheets';
import type { ElectionYear } from '~/services/googleTrends';

export const POLLS_TAB = 'gold_pesquisas_candidato_temporal';

/** One electoral-poll observation for a candidate on a given field date. */
export type PollRow = {
  date: string;
  electionYear: ElectionYear;
  candidate: string;
  candidateNormalized: string;
  percent: number | null;
  institute: string;
  pollId: string;
};

/** Raw shape as it arrives from the gold spreadsheet (snake_case headers). */
type RawPollRow = {
  ano_eleicao: string;
  data_referencia: string;
  instituto_pesquisa: string;
  pesquisa_id: string;
  cenario_id: string;
  nome_candidato: string;
  nome_candidato_normalizado: string;
  partido: string;
  percentual_numero: string;
  percentual_original: string;
  tamanho_amostra: string;
  margem_erro: string;
  fonte_url: string;
  fonte_website: string;
};

/** Absence stays null — a poll percentage is never coerced to zero. */
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

/** Maps the integer election year of the poll table to the app's ElectionYear. */
export function electionYearFromAno(ano: string): ElectionYear {
  const normalized = ano.trim();

  return normalized === '2026' ? 'current' : (normalized as ElectionYear);
}

function mapRow(raw: RawPollRow): PollRow {
  return {
    date: raw.data_referencia,
    electionYear: electionYearFromAno(raw.ano_eleicao),
    candidate: raw.nome_candidato,
    candidateNormalized: raw.nome_candidato_normalizado,
    percent: parseNullableNumber(raw.percentual_numero),
    institute: raw.instituto_pesquisa,
    pollId: raw.pesquisa_id,
  };
}

/** Fetches and parses the gold candidate-temporal poll table. */
export async function fetchPollRows(): Promise<PollRow[]> {
  const csv = await fetchSheetCsv(POLLS_TAB);
  const rows = parseCsv<RawPollRow>(csv);

  return rows.filter((row) => row.data_referencia && row.nome_candidato).map(mapRow);
}
