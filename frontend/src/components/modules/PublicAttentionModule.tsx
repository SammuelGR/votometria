import { useMemo, useState } from 'react';

import AttentionTimelineChart from '~/components/charts/AttentionTimelineChart';
import {
  CandidateMultiSelect,
  MetricCard,
  ModuleHeader,
  ModulePanel,
  PlaceholderChart,
  SegmentedControl,
  SourceBadge,
} from '~/components/ui';
import { EVENTS_DISCLAIMER_2026 } from '~/data/electionEvents';
import { activePresetKey, periodsForYear } from '~/data/electionPeriods';
import { useGoogleTrends } from '~/fetchers/hooks/useGoogleTrends';
import type { ElectionYear, TrendsMetric } from '~/services/googleTrends';
import { cn } from '~/utils/cn';
import {
  buildTimeline,
  detectPeaks,
  filterByRange,
  filterByYear,
  highestPeak,
  termsByMean,
  topCandidatesByMean,
  type DateRange,
} from '~/utils/trends';

const metricOptions = [
  { label: 'Reescalado', value: 'interestScaled' },
  { label: 'Bruto', value: 'interestRaw' },
];

const EMPTY_RANGE: DateRange = {};

type PublicAttentionModuleProps = {
  electionYear: ElectionYear;
};

export default function PublicAttentionModule({ electionYear }: PublicAttentionModuleProps) {
  const { data, isLoading, isError } = useGoogleTrends();
  const [metric, setMetric] = useState<TrendsMetric>('interestScaled');
  const [showEvents, setShowEvents] = useState(true);
  const [selection, setSelection] = useState<{ terms: string[]; year: ElectionYear | null }>({
    terms: [],
    year: null,
  });
  const [rangeState, setRangeState] = useState<{ range: DateRange; year: ElectionYear | null }>({
    range: {},
    year: null,
  });

  const yearRows = useMemo(() => filterByYear(data ?? [], electionYear), [data, electionYear]);
  const presets = periodsForYear(electionYear);
  const range = rangeState.year === electionYear ? rangeState.range : EMPTY_RANGE;
  const rows = useMemo(() => filterByRange(yearRows, range), [yearRows, range]);

  const orderedTerms = useMemo(() => termsByMean(rows, metric), [rows, metric]);
  const defaultSelection = useMemo(() => topCandidatesByMean(rows, metric, 4), [rows, metric]);
  const selected = selection.year === electionYear ? selection.terms : defaultSelection;

  const topAttention = orderedTerms.find((term) => selected.includes(term)) ?? '—';
  const peak = useMemo(() => {
    const timeline = buildTimeline(rows, selected, metric);

    return highestPeak(detectPeaks(timeline, selected, electionYear));
  }, [rows, selected, metric, electionYear]);

  function handleSelectionChange(terms: string[]) {
    setSelection({ terms, year: electionYear });
  }

  function applyPreset(key: string) {
    const preset = presets.find((option) => option.key === key);

    if (preset) {
      setRangeState({ range: preset.range, year: electionYear });
    }
  }

  return (
    <ModulePanel>
      <div className="flex flex-col gap-5">
        <ModuleHeader
          badges={<SourceBadge label="Google Trends" tone="attention" />}
          title="Atenção pública"
        />

        <div className="flex flex-wrap items-end gap-4">
          <CandidateMultiSelect
            label="Candidatos"
            onChange={handleSelectionChange}
            options={orderedTerms}
            selected={selected}
          />

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
            <span className="font-mono text-[11px] text-muted uppercase tracking-wide">Eventos</span>

            <button
              aria-pressed={showEvents}
              className={cn(
                'border-line-strong cursor-pointer font-mono rounded-md border px-3 py-1.5 text-xs uppercase tracking-wide transition-colors',
                showEvents ? 'bg-foreground text-surface' : 'bg-surface text-muted hover:bg-navigation',
              )}
              onClick={() => setShowEvents((value) => !value)}
              type="button"
            >
              {showEvents ? 'Visíveis' : 'Ocultos'}
            </button>
          </div>
        </div>

        {isLoading ? (
          <PlaceholderChart label="Carregando dados do Google Trends…" />
        ) : isError ? (
          <PlaceholderChart label="Falha ao carregar os dados. Verifique a planilha e o VITE_GOOGLE_SHEETS_ID." />
        ) : selected.length === 0 || rows.length === 0 ? (
          <PlaceholderChart label="Selecione ao menos um candidato com dados no período." />
        ) : (
          <AttentionTimelineChart
            metric={metric}
            rows={rows}
            showEvents={showEvents}
            terms={selected}
            year={electionYear}
          />
        )}

        <div className="gap-3 grid sm:grid-cols-2">
          <MetricCard text={topAttention} title="Maior atenção" />

          <MetricCard text={peak ? `${peak.term} · ${Math.round(peak.value)}` : '—'} title="Maior pico" />
        </div>

        <div className="flex flex-col gap-1">
          <p className="font-mono text-[11px] text-muted">
            Índice relativo, reescalado por candidato para comparação aproximada no mesmo ano. Não comparar entre anos
            diferentes.
          </p>

          {electionYear === 'current' ? (
            <p className="font-mono text-[11px] text-muted">{EVENTS_DISCLAIMER_2026}</p>
          ) : null}
        </div>
      </div>
    </ModulePanel>
  );
}
