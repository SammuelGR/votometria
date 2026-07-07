import { fetchSheetCsv, parseCsv } from '~/services/sheets';

export type TseElectionYear = '2018' | '2022';
export type TseVoteRound = '1' | '2';

export type TseVoteRow = {
  electionYear: TseElectionYear;
  round: TseVoteRound;
  candidate: string;
  votes: number;
};

type RawTseVoteRow = {
  NM_URNA_CANDIDATO?: string;
  QT_VOTOS_NOMINAIS?: string;
};

function parseNumber(value: string | undefined): number {
  if (!value) {
    return 0;
  }

  // Remove os pontos de milhar e troca a vírgula decimal por ponto
  const normalized = value.replace(/\./g, '').replace(',', '.').trim();
  const parsed = Number(normalized);

  return Number.isFinite(parsed) ? parsed : 0;
}

export function getTseVotesTabName(year: TseElectionYear, round: TseVoteRound): string {
  // Reads the already-processed TSE tab published in Google Sheets.
  return `proc_tse_${year}_votes_t${round}`;
}

export async function fetchTseVotesRows(year: TseElectionYear, round: TseVoteRound): Promise<TseVoteRow[]> {
  const csv = await fetchSheetCsv(getTseVotesTabName(year, round));
  const rows = parseCsv<RawTseVoteRow>(csv);

  return rows
    .filter((row) => row.NM_URNA_CANDIDATO && row.NM_URNA_CANDIDATO.trim())
    .filter((row) => row.NM_URNA_CANDIDATO?.trim().toUpperCase() !== 'SOMA')
    .map((row) => ({
      electionYear: year,
      round,
      candidate: row.NM_URNA_CANDIDATO?.trim() ?? '—',
      votes: parseNumber(row.QT_VOTOS_NOMINAIS),
    }))
    // Ordena do maior número de votos para o menor
    .sort((left, right) => right.votes - left.votes);
}