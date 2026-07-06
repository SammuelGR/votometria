import { fetchSheetCsv, parseCsv } from '~/services/sheets';

export const TSE_STATE_DIST_TABS = {
  '2018': {
    t1: 'proc_tse_2018_state_dist_t1',
    t2: 'proc_tse_2018_state_dist_t2',
  },
  '2022': {
    t1: 'proc_tse_2022_state_dist_t1',
    t2: 'proc_tse_2022_state_dist_t2',
  },
} as const;

export type TseStateDistYear = keyof typeof TSE_STATE_DIST_TABS;
export type TseStateDistTurn = 't1' | 't2';

export type TseStateDistCandidate = {
  name: string;
  votes: number;
};

export type TseStateDistState = {
  uf: string;
  candidates: TseStateDistCandidate[];
  winner: TseStateDistCandidate;
};

export type TseStateDistRow = {
  uf: string;
  candidates: TseStateDistCandidate[];
  winner: TseStateDistCandidate;
};

type RawTseStateDistRow = Record<string, string>;

function parseNumber(value: string | undefined): number {
  const parsed = Number(value);

  return Number.isFinite(parsed) ? parsed : 0;
}

function normalizeUf(value: string | undefined): string {
  return (value ?? '').trim().toUpperCase();
}

function isIgnoredColumn(key: string): boolean {
  return ['UF', 'TOTAL', 'SOMA', ''].includes(key.trim().toUpperCase());
}

function buildStateRows(rows: RawTseStateDistRow[]): TseStateDistRow[] {
  const stateRows = rows.filter((row) => {
    const uf = normalizeUf(row.UF);

    return uf !== '' && uf !== 'UF';
  });

  return stateRows.map((row) => {
    const uf = normalizeUf(row.UF);
    const candidateEntries = Object.entries(row)
      .filter(([key]) => !isIgnoredColumn(key))
      .filter(([key]) => key !== 'UF')
      .map(([name, value]) => ({
        name: name.trim(),
        votes: parseNumber(value),
      }))
      .filter((candidate) => candidate.name.length > 0);

    const sortedCandidates = [...candidateEntries].sort((a, b) => b.votes - a.votes);
    const winner = sortedCandidates[0] ?? { name: '—', votes: 0 };

    return {
      uf,
      candidates: sortedCandidates,
      winner,
    };
  });
}

/** Fetches and parses the state vote distribution table for a given election year and round. */
export async function fetchTseStateDistributionRows(
  year: TseStateDistYear = '2022',
  turn: TseStateDistTurn = 't2',
): Promise<TseStateDistRow[]> {
  const tabName = TSE_STATE_DIST_TABS[year][turn];
  const csv = await fetchSheetCsv(tabName);
  const rows = parseCsv<RawTseStateDistRow>(csv);

  return buildStateRows(rows);
}
