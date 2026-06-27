import type { ElectionYear } from '~/services/googleTrends';
import type { DateRange } from '~/utils/trends';

/**
 * Presets de período para recortar os dashboards de Google Trends.
 *
 * A coleta é sempre do ano inteiro (ver docs/google_trends_metodologia.md); estes
 * presets são apenas filtros de leitura. "Ano completo" usa um range vazio, que os
 * módulos resolvem para a extensão total dos dados. As janelas de "Campanha oficial"
 * vão do início legal da propaganda (16/08) até o segundo turno — datas verificadas
 * do TSE para 2018 e 2022.
 */
export type PeriodPreset = {
  key: string;
  label: string;
  range: DateRange;
};

const FULL_YEAR: PeriodPreset = { key: 'full', label: 'Ano completo', range: {} };

export const ELECTION_PERIODS: Record<ElectionYear, PeriodPreset[]> = {
  '2018': [
    FULL_YEAR,
    { key: 'campaign', label: 'Campanha oficial', range: { start: '2018-08-16', end: '2018-10-28' } },
  ],
  '2022': [
    FULL_YEAR,
    { key: 'campaign', label: 'Campanha oficial', range: { start: '2022-08-16', end: '2022-10-30' } },
  ],
  current: [FULL_YEAR],
};

/** Presets disponíveis para o ano; sempre inclui ao menos "Ano completo". */
export function periodsForYear(year: ElectionYear): PeriodPreset[] {
  return ELECTION_PERIODS[year] ?? [FULL_YEAR];
}

/** Compara dois ranges considerando campos ausentes como equivalentes a vazio. */
export function rangesEqual(a: DateRange, b: DateRange): boolean {
  return (a.start ?? '') === (b.start ?? '') && (a.end ?? '') === (b.end ?? '');
}

/** Chave do preset que casa com o range atual, ou '' quando for personalizado. */
export function activePresetKey(year: ElectionYear, range: DateRange): string {
  return periodsForYear(year).find((preset) => rangesEqual(preset.range, range))?.key ?? '';
}
