import { useMemo, useState } from 'react';

import ShareOfSearchChart from '~/components/charts/ShareOfSearchChart';
import {
  MetricCard,
  ModuleHeader,
  ModulePanel,
  MultiSelect,
  PlaceholderChart,
  SegmentedControl,
  SourceBadge,
} from '~/components/ui';
import { activePresetKey, periodsForYear } from '~/data/electionPeriods';
import { useGoogleTrends } from '~/fetchers/hooks/useGoogleTrends';
import type { ElectionYear, TrendsMetric } from '~/services/googleTrends';
import {
  classifyConcentration,
  type DateRange,
  dateExtent,
  filterByYear,
  shareOfSearch,
  termsByMean,
  top2Concentration,
} from '~/utils/trends';

const INITIAL_SELECTED_CANDIDATE_LIMIT = 7;
const EMPTY_DATE_RANGE: DateRange = {};

const YEAR_OPTIONS = [
  { label: '2018', value: '2018' },
  { label: '2022', value: '2022' },
  { label: '2026', value: 'current' },
];

// Default to the anchor-rescaled metric. The raw toggle is an audit aid: for
// candidates collected in the same batch (e.g. Lula and Bolsonaro, both in
// batch_01) raw and scaled coincide and are directly comparable.
const METRIC_OPTIONS = [
  { label: 'Reescalado', value: 'interestScaled' },
  { label: 'Bruto', value: 'interestRaw' },
];

const formatFullDate = (date?: string): string => {
  if (!date) {
    return '—';
  }

  const [year, month, day] = date.split('-');

  return `${day}/${month}/${year}`;
};

export default function ShareOfSearch() {
  const { data, isLoading, isError } = useGoogleTrends();
  const [electionYear, setElectionYear] = useState<ElectionYear>('current');
  const [metric, setMetric] = useState<TrendsMetric>('interestScaled');
  const [candidateSelection, setCandidateSelection] = useState<{ terms: string[]; year: ElectionYear | null }>({
    terms: [],
    year: null,
  });
  const [dateRangeSelection, setDateRangeSelection] = useState<{ range: DateRange; year: ElectionYear | null }>({
    range: {},
    year: null,
  });

  const yearRows = useMemo(() => filterByYear(data ?? [], electionYear), [data, electionYear]);
  const orderedCandidateTerms = useMemo(() => termsByMean(yearRows, metric), [yearRows, metric]);
  const dateRangeExtent = useMemo(() => dateExtent(yearRows), [yearRows]);
  const periodPresets = periodsForYear(electionYear);

  const candidateOptions = orderedCandidateTerms.map((term) => ({ label: term, value: term }));
  const initialCandidateValues = orderedCandidateTerms.slice(0, INITIAL_SELECTED_CANDIDATE_LIMIT);
  const selectedCandidateValues =
    candidateSelection.year === electionYear ? candidateSelection.terms : initialCandidateValues;

  const selectedDateRange = dateRangeSelection.year === electionYear ? dateRangeSelection.range : EMPTY_DATE_RANGE;
  const periodStartDate = selectedDateRange.start ?? dateRangeExtent.start;
  const periodEndDate = selectedDateRange.end ?? dateRangeExtent.end;

  const candidateShares = useMemo(() => {
    const termsForShare =
      candidateSelection.year === electionYear
        ? candidateSelection.terms.length > 0
          ? candidateSelection.terms
          : orderedCandidateTerms
        : orderedCandidateTerms.slice(0, INITIAL_SELECTED_CANDIDATE_LIMIT);

    return shareOfSearch(yearRows, termsForShare, metric, { start: periodStartDate, end: periodEndDate });
  }, [candidateSelection, electionYear, metric, orderedCandidateTerms, periodEndDate, periodStartDate, yearRows]);

  const concentration = top2Concentration(candidateShares);
  const concentrationLabel = classifyConcentration(concentration);
  const periodLabel = `período de ${formatFullDate(periodStartDate)} a ${formatFullDate(periodEndDate)}`;

  const presetOptions = periodPresets.map((preset) => ({ label: preset.label, value: preset.key }));
  const activePreset = activePresetKey(electionYear, selectedDateRange);
  const hasChartData = candidateShares.length > 0 && yearRows.length > 0;

  const handlePeriodChange = (field: keyof DateRange, value: string) => {
    setDateRangeSelection({
      range: { ...selectedDateRange, [field]: value },
      year: electionYear,
    });
  };

  const handlePresetChange = (key: string) => {
    const preset = periodPresets.find((option) => option.key === key);

    if (preset) {
      setDateRangeSelection({ range: preset.range, year: electionYear });
    }
  };

  return (
    <ModulePanel>
      <div className="flex h-full flex-col gap-5">
        <ModuleHeader badges={<SourceBadge label="Google Trends" tone="attention" />} title="Share of Search" />

        <div className="flex flex-wrap items-end gap-4">
          <SegmentedControl
            label="Eleição"
            onChange={(value) => setElectionYear(value as ElectionYear)}
            options={YEAR_OPTIONS}
            value={electionYear}
          />

          <SegmentedControl
            label="Índice"
            onChange={(value) => setMetric(value as TrendsMetric)}
            options={METRIC_OPTIONS}
            value={metric}
          />

          {periodPresets.length > 1 ? (
            <SegmentedControl
              label="Janela"
              onChange={handlePresetChange}
              options={presetOptions}
              value={activePreset}
            />
          ) : null}

          <div className="flex flex-col gap-2">
            <span className="font-mono text-[11px] text-muted uppercase tracking-wide">Período</span>

            <div className="flex items-center gap-2">
              <input
                className="bg-surface border-border h-9 cursor-pointer rounded-md border px-2 font-mono text-foreground text-xs"
                max={periodEndDate}
                min={dateRangeExtent.start}
                onChange={(event) => handlePeriodChange('start', event.target.value)}
                type="date"
                value={periodStartDate ?? ''}
              />

              <span className="text-muted text-xs">até</span>

              <input
                className="bg-surface border-border h-9 cursor-pointer rounded-md border px-2 font-mono text-foreground text-xs"
                max={dateRangeExtent.end}
                min={periodStartDate}
                onChange={(event) => handlePeriodChange('end', event.target.value)}
                type="date"
                value={periodEndDate ?? ''}
              />
            </div>
          </div>

          <MultiSelect
            disabled={isError}
            label="Candidatos"
            loading={isLoading}
            onChange={(terms) => setCandidateSelection({ terms, year: electionYear })}
            options={candidateOptions}
            value={selectedCandidateValues}
          />
        </div>

        {isLoading ? (
          <PlaceholderChart className="min-h-56" label="Carregando dados do Google Trends…" />
        ) : isError ? (
          <PlaceholderChart
            className="min-h-56"
            label="Falha ao carregar os dados. Verifique a planilha e o VITE_GOOGLE_SHEETS_ID."
          />
        ) : hasChartData ? (
          <ShareOfSearchChart periodLabel={periodLabel} shares={candidateShares} />
        ) : (
          <PlaceholderChart className="min-h-56" label="Sem dados para o período selecionado." />
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
