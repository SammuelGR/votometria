import { useMemo, useState } from 'react';

import AttentionTimelineChart from '~/components/charts/AttentionTimelineChart';
import {
  MetricCard,
  ModuleHeader,
  ModulePanel,
  MultiSelect,
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

const yearOptions = [
  { label: '2018', value: '2018' },
  { label: '2022', value: '2022' },
  { label: '2026', value: 'current' },
];

const EMPTY_RANGE: DateRange = {};
const INITIAL_SELECTED_CANDIDATE_LIMIT = 4;
const METRIC: TrendsMetric = 'interestRaw';

export default function PublicAttention() {
  const { data, isLoading, isError } = useGoogleTrends();
  const [electionYear, setElectionYear] = useState<ElectionYear>('current');
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

  const orderedTerms = useMemo(() => termsByMean(rows, METRIC), [rows]);
  const candidateOptions = orderedTerms.map((term) => ({ label: term, value: term }));
  const initialSelection = useMemo(() => topCandidatesByMean(rows, METRIC, INITIAL_SELECTED_CANDIDATE_LIMIT), [rows]);
  const selectedValues = selection.year === electionYear ? selection.terms : initialSelection;
  const selectedTerms = selectedValues.length > 0 ? selectedValues : orderedTerms;

  const topAttention = orderedTerms.find((term) => selectedTerms.includes(term)) ?? '—';
  const peak = useMemo(() => {
    const timeline = buildTimeline(rows, selectedTerms, METRIC);

    return highestPeak(detectPeaks(timeline, selectedTerms, electionYear));
  }, [rows, selectedTerms, electionYear]);

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
        <ModuleHeader badges={<SourceBadge label="Google Trends" tone="attention" />} title="Atenção pública" />

        <div className="flex flex-wrap items-end gap-4">
          <SegmentedControl
            label="Eleição"
            onChange={(value) => setElectionYear(value as ElectionYear)}
            options={yearOptions}
            value={electionYear}
          />

          <MultiSelect
            disabled={isError}
            label="Candidatos"
            loading={isLoading}
            onChange={handleSelectionChange}
            options={candidateOptions}
            value={selectedValues}
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
        ) : rows.length === 0 || selectedTerms.length === 0 ? (
          <PlaceholderChart label="Selecione ao menos um candidato com dados no período." />
        ) : (
          <AttentionTimelineChart
            metric={METRIC}
            rows={rows}
            showEvents={showEvents}
            terms={selectedTerms}
            year={electionYear}
          />
        )}

        <div className="gap-3 grid sm:grid-cols-2">
          <MetricCard text={topAttention} title="Maior atenção" />

          <MetricCard text={peak ? `${peak.term} · ${Math.round(peak.value)}` : '—'} title="Maior pico" />
        </div>

        <div className="flex flex-col gap-1">
          <p className="font-mono text-[11px] text-muted">
            Índice bruto de interesse (Google Trends), normalizado por lote de coleta; comparável apenas entre
            candidatos do mesmo lote. Não comparar entre anos diferentes.
          </p>

          {electionYear === 'current' ? (
            <p className="font-mono text-[11px] text-muted">{EVENTS_DISCLAIMER_2026}</p>
          ) : null}
        </div>
      </div>
    </ModulePanel>
  );
}
