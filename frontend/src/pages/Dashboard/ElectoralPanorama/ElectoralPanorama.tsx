import { useMemo, useState } from 'react';

import ElectoralPanoramaChart from '~/components/charts/ElectoralPanoramaChart';
import {
  ModuleHeader,
  ModulePanel,
  MultiSelect,
  PlaceholderChart,
  SegmentedControl,
  SourceBadge,
} from '~/components/ui';
import { activePresetKey, periodsForYear } from '~/data/electionPeriods';
import { useGoogleTrends } from '~/fetchers/hooks/useGoogleTrends';
import { useWeeklyMarketExpectations } from '~/fetchers/hooks/useWeeklyMarketExpectations';
import { usePesquisasMensais } from '~/fetchers/hooks/usePesquisasMensais';
import type { ElectionYear, TrendsMetric } from '~/services/googleTrends';
import { buildElectoralPanoramaSeries } from '~/utils/electoralPanorama';
import { filterPollMonthlyByYear } from '~/utils/pesquisasMensais';
import { filterByYear, isWithinRange, termsByMean, type DateRange } from '~/utils/trends';

const yearOptions = [
  { label: '2018', value: '2018' },
  { label: '2022', value: '2022' },
  { label: '2026', value: 'current' },
];

const EMPTY_RANGE: DateRange = {};
const METRIC: TrendsMetric = 'interestRaw';

export default function ElectoralPanorama() {
  const trends = useGoogleTrends();
  const polls = usePesquisasMensais();

  const [electionYear, setElectionYear] = useState<ElectionYear>('current');
  const [selection, setSelection] = useState<{ candidate: string | null; year: ElectionYear | null }>({
    candidate: null,
    year: null,
  });
  const [rangeState, setRangeState] = useState<{ range: DateRange; year: ElectionYear | null }>({
    range: {},
    year: null,
  });

  const isLoading = trends.isLoading || polls.isLoading;
  const isError = trends.isError || polls.isError;

  const presets = periodsForYear(electionYear);
  const range = rangeState.year === electionYear ? rangeState.range : EMPTY_RANGE;

  const yearTrendsRows = useMemo(() => filterByYear(trends.data ?? [], electionYear), [trends.data, electionYear]);
  const scopedTrendsRows = useMemo(
    () => yearTrendsRows.filter((row) => isWithinRange(row.date, range)),
    [yearTrendsRows, range],
  );
  const orderedTerms = useMemo(() => termsByMean(scopedTrendsRows, METRIC), [scopedTrendsRows]);
  const candidateOptions = orderedTerms.map((term) => ({ label: term, value: term }));

  const activeCandidate =
    selection.year === electionYear && selection.candidate ? selection.candidate : (orderedTerms[0] ?? null);

  const marketExpectations = useWeeklyMarketExpectations(activeCandidate, {
    enabled: electionYear === 'current' && Boolean(activeCandidate),
  });

  const yearPollRows = useMemo(
    () => filterPollMonthlyByYear(polls.data ?? [], electionYear),
    [polls.data, electionYear],
  );

  const points = useMemo(() => {
    if (!activeCandidate) {
      return [];
    }

    return buildElectoralPanoramaSeries(
      yearTrendsRows,
      yearPollRows,
      activeCandidate,
      electionYear,
      range,
      electionYear === 'current' ? (marketExpectations.data?.points ?? []) : [],
    );
  }, [yearTrendsRows, yearPollRows, activeCandidate, electionYear, range, marketExpectations.data?.points]);

  const hasData = points.some((point) => point.attention != null || point.polling != null);
  const hasPolls = points.some((point) => point.polling != null);

  // Single-candidate selector via MultiSelect (radio-like): keep the option the
  // user just checked; unchecking the current one keeps it (a candidate is required).
  function handleCandidateChange(values: string[]) {
    const next = values.find((value) => value !== activeCandidate) ?? values[0] ?? activeCandidate;

    if (next) {
      setSelection({ candidate: next, year: electionYear });
    }
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
          badges={
            <>
              <SourceBadge label="Google Trends" tone="attention" />

              <SourceBadge label="Pesquisas eleitorais" tone="positive" />

              <SourceBadge label="Polymarket" tone="market" />
            </>
          }
          title="Panorama eleitoral"
        />

        <div className="flex flex-wrap items-end gap-4">
          <SegmentedControl
            label="Eleição"
            onChange={(value) => setElectionYear(value as ElectionYear)}
            options={yearOptions}
            value={electionYear}
          />

          <MultiSelect
            allLabel="Selecione um candidato"
            disabled={isError}
            label="Candidato"
            loading={isLoading}
            onChange={handleCandidateChange}
            options={candidateOptions}
            value={activeCandidate ? [activeCandidate] : []}
          />

          {presets.length > 1 ? (
            <SegmentedControl
              label="Janela"
              onChange={applyPreset}
              options={presets.map((preset) => ({ label: preset.label, value: preset.key }))}
              value={activePresetKey(electionYear, range)}
            />
          ) : null}
        </div>

        {isLoading ? (
          <PlaceholderChart label="Carregando dados de atenção e pesquisas…" />
        ) : isError ? (
          <PlaceholderChart label="Falha ao carregar os dados. Verifique a planilha e o VITE_GOOGLE_SHEETS_ID." />
        ) : !activeCandidate || !hasData ? (
          <PlaceholderChart label="Selecione um candidato com dados de atenção ou pesquisa no período." />
        ) : (
          <ElectoralPanoramaChart candidate={activeCandidate} points={points} year={electionYear} />
        )}

        <div className="flex flex-col gap-1">
          {!hasPolls && activeCandidate ? (
            <p className="font-mono text-[11px] text-muted">
              Sem pesquisas eleitorais para “{activeCandidate}” neste recorte; apenas a atenção pública é exibida.
            </p>
          ) : null}
        </div>
      </div>
    </ModulePanel>
  );
}
