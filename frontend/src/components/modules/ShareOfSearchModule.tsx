import { useMemo, useState } from 'react';

import ShareOfSearchChart from '~/components/charts/ShareOfSearchChart';
import {
  CandidateMultiSelect,
  MetricCard,
  ModuleHeader,
  ModulePanel,
  PlaceholderChart,
  SegmentedControl,
  SourceBadge,
} from '~/components/ui';
import { activePresetKey, periodsForYear } from '~/data/electionPeriods';
import { useGoogleTrends } from '~/fetchers/hooks/useGoogleTrends';
import type { ElectionYear, TrendsMetric } from '~/services/googleTrends';
import {
  classifyConcentration,
  dateExtent,
  filterByYear,
  shareOfSearch,
  termsByMean,
  top2Concentration,
  type DateRange,
} from '~/utils/trends';

function formatFullDate(date?: string): string {
  if (!date) {
    return '—';
  }

  const [year, month, day] = date.split('-');

  return `${day}/${month}/${year}`;
}

type ShareOfSearchModuleProps = {
  electionYear: ElectionYear;
};

// Default to the anchor-rescaled metric. The raw toggle is an audit aid: for
// candidates collected in the same batch (e.g. Lula and Bolsonaro, both in
// batch_01) raw and scaled coincide and are directly comparable.
const metricOptions = [
  { label: 'Reescalado', value: 'interestScaled' },
  { label: 'Bruto', value: 'interestRaw' },
];

export default function ShareOfSearchModule({ electionYear }: ShareOfSearchModuleProps) {
  const { data, isLoading, isError } = useGoogleTrends();
  const [metric, setMetric] = useState<TrendsMetric>('interestScaled');
  const [selection, setSelection] = useState<{ terms: string[]; year: ElectionYear | null }>({
    terms: [],
    year: null,
  });
  const [rangeState, setRangeState] = useState<{ range: DateRange; year: ElectionYear | null }>({
    range: {},
    year: null,
  });

  const rows = useMemo(() => filterByYear(data ?? [], electionYear), [data, electionYear]);
  const orderedTerms = useMemo(() => termsByMean(rows, metric), [rows, metric]);
  const extent = useMemo(() => dateExtent(rows), [rows]);

  const selected = selection.year === electionYear ? selection.terms : orderedTerms;
  const range = rangeState.year === electionYear ? rangeState.range : {};
  const startDate = range.start ?? extent.start;
  const endDate = range.end ?? extent.end;

  const shares = useMemo(
    () => shareOfSearch(rows, selected, metric, { start: startDate, end: endDate }),
    [rows, selected, metric, startDate, endDate],
  );

  const concentration = top2Concentration(shares);
  const concentrationLabel = classifyConcentration(concentration);
  const periodLabel = `período de ${formatFullDate(startDate)} a ${formatFullDate(endDate)}`;

  const presets = periodsForYear(electionYear);

  function setRange(next: DateRange) {
    setRangeState({ range: next, year: electionYear });
  }

  function applyPreset(key: string) {
    const preset = presets.find((option) => option.key === key);

    if (preset) {
      setRange(preset.range);
    }
  }

  return (
    <ModulePanel>
      <div className="flex h-full flex-col gap-5">
        <ModuleHeader
          badges={<SourceBadge label="Google Trends" tone="attention" />}
          title="Share of Search"
        />

        <div className="flex flex-wrap items-end gap-4">
          <SegmentedControl
            label="Índice"
            onChange={(value) => setMetric(value as TrendsMetric)}
            options={metricOptions}
            value={metric}
          />

          {presets.length > 1 ? (
            <SegmentedControl
              label="Janela"
              onChange={applyPreset}
              options={presets.map((preset) => ({ label: preset.label, value: preset.key }))}
              value={activePresetKey(electionYear, range)}
            />
          ) : null}

          <div className="flex flex-col gap-2">
            <span className="font-mono text-[11px] text-muted uppercase tracking-wide">Período</span>

            <div className="flex items-center gap-2">
              <input
                className="bg-surface border-border h-9 cursor-pointer rounded-md border px-2 font-mono text-foreground text-xs"
                max={endDate}
                min={extent.start}
                onChange={(event) => setRange({ ...range, start: event.target.value })}
                type="date"
                value={startDate ?? ''}
              />

              <span className="text-muted text-xs">até</span>

              <input
                className="bg-surface border-border h-9 cursor-pointer rounded-md border px-2 font-mono text-foreground text-xs"
                max={extent.end}
                min={startDate}
                onChange={(event) => setRange({ ...range, end: event.target.value })}
                type="date"
                value={endDate ?? ''}
              />
            </div>
          </div>

          <CandidateMultiSelect
            label="Candidatos"
            onChange={(terms) => setSelection({ terms, year: electionYear })}
            options={orderedTerms}
            selected={selected}
          />
        </div>

        {isLoading ? (
          <PlaceholderChart className="min-h-56" label="Carregando dados do Google Trends…" />
        ) : isError ? (
          <PlaceholderChart
            className="min-h-56"
            label="Falha ao carregar os dados. Verifique a planilha e o VITE_GOOGLE_SHEETS_ID."
          />
        ) : shares.length === 0 || rows.length === 0 ? (
          <PlaceholderChart className="min-h-56" label="Sem dados para o período selecionado." />
        ) : (
          <ShareOfSearchChart periodLabel={periodLabel} shares={shares} />
        )}

        <div className="gap-3 grid">
          <MetricCard title="Concentração Top 2" value={`${concentration.toFixed(0)}% · ${concentrationLabel}`} />
        </div>

        <p className="font-mono text-[11px] text-muted">
          Share = média de interesse do candidato no período ÷ soma das médias de todos os selecionados. Índice
          relativo; não comparar entre anos diferentes.
        </p>
      </div>
    </ModulePanel>
  );
}
