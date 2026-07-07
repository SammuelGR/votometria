import { fetchSheetCsv, parseCsv } from '~/services/sheets';

export const TSE_COMPARISON_TABS = {
  '2018': 'proc_tse_2018_comparison',
  '2022': 'proc_tse_2022_comparison',
} as const;

export type TseComparisonYear = keyof typeof TSE_COMPARISON_TABS;

export interface TseComparisonRow {
  NM_URNA_CANDIDATO: string;
  QT_VOTOS_1T: number;
  QT_VOTOS_2T: number;
  DIFERENCA: number;
}

type RawTseComparisonRow = {
  NM_URNA_CANDIDATO: string;
  QT_VOTOS_1T: string;
  QT_VOTOS_2T: string;
  DIFERENCA: string;
};

function parseNumber(value: string | undefined): number {
  const parsed = Number(value);

  return Number.isFinite(parsed) ? parsed : 0;
}

function mapRow(raw: RawTseComparisonRow): TseComparisonRow {
  return {
    NM_URNA_CANDIDATO: raw.NM_URNA_CANDIDATO,
    QT_VOTOS_1T: parseNumber(raw.QT_VOTOS_1T),
    QT_VOTOS_2T: parseNumber(raw.QT_VOTOS_2T),
    DIFERENCA: parseNumber(raw.DIFERENCA),
  };
}

export async function fetchTseComparisonRows(year: TseComparisonYear = '2022'): Promise<TseComparisonRow[]> {
  const csv = await fetchSheetCsv(TSE_COMPARISON_TABS[year]);
  const rows = parseCsv<RawTseComparisonRow>(csv);

  return rows.filter((row) => row.NM_URNA_CANDIDATO).map(mapRow);
}
