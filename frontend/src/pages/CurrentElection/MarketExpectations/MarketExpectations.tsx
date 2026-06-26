import { useState } from 'react';

import {
  IntervalSelector,
  MetricCard,
  ModuleHeader,
  ModulePanel,
  MultiSelect,
  PlaceholderChart,
  SourceBadge,
} from '~/components/ui';
import { useMarketExpectationFilters } from '~/fetchers/hooks/useMarketExpectationFilters';
import { useMarketExpectations } from '~/fetchers/hooks/useMarketExpectations';
import type { MarketExpectationInterval } from '~/models/marketExpectations';
import { EMPTY_VALUE, formatProbability } from '~/utils/format';

const DEFAULT_INTERVALS: MarketExpectationInterval[] = ['1h', '4h', '1d', '1w'];

const INTERVAL_LABELS: Partial<Record<MarketExpectationInterval, string>> = {
  '1w': '1 sem.',
};

export default function MarketExpectations() {
  const [selectedCandidates, setSelectedCandidates] = useState<string[]>([]);
  const [selectedInterval, setSelectedInterval] = useState<MarketExpectationInterval>('1h');

  const filtersQuery = useMarketExpectationFilters();

  const selectedCandidateCatalogIds = selectedCandidates.map(Number);
  const marketExpectationsQuery = useMarketExpectations({
    candidateCatalogIds: selectedCandidateCatalogIds.length > 0 ? selectedCandidateCatalogIds : undefined,
    interval: selectedInterval,
  });

  const isFiltersLoading = filtersQuery.isLoading;
  const isSeriesLoading = marketExpectationsQuery.isLoading;
  const hasError = filtersQuery.isError || marketExpectationsQuery.isError;
  const isLoading = isFiltersLoading || isSeriesLoading;
  const hasSeries = (marketExpectationsQuery.data?.series.length ?? 0) > 0;

  const candidateOptions =
    filtersQuery.data?.candidates
      .toSorted((firstCandidate, secondCandidate) =>
        firstCandidate.displayName.localeCompare(secondCandidate.displayName),
      )
      .map((candidate) => ({
        label: candidate.displayName,
        value: String(candidate.candidateCatalogId),
      })) ?? [];

  const intervals = filtersQuery.data?.intervals ?? DEFAULT_INTERVALS;
  const intervalOptions = intervals.map((interval) => ({
    label: INTERVAL_LABELS[interval] ?? interval,
    value: interval,
  }));

  const summary = marketExpectationsQuery.data?.summary;
  const currentLeaderText = summary?.currentLeader?.displayName ?? EMPTY_VALUE;
  const currentLeaderValue = formatProbability(summary?.currentLeader?.probability);
  const leaderMarginValue = formatProbability(summary?.leaderMargin?.value);
  const largestChange = summary?.largestChange;
  const largestChangeText = largestChange?.displayName ?? EMPTY_VALUE;
  const largestChangeValue = formatProbability(largestChange?.value, { signDisplay: 'exceptZero' });
  const largestChangeVariant =
    largestChange && largestChange.value > 0
      ? 'positive'
      : largestChange && largestChange.value < 0
        ? 'negative'
        : 'default';

  const chartFeedback = hasError
    ? 'Não foi possível carregar os dados de expectativa de mercado.'
    : isLoading
      ? 'Carregando dados de expectativa de mercado...'
      : hasSeries
        ? null
        : 'Nenhum dado encontrado para os filtros selecionados.';

  return (
    <ModulePanel>
      <div className="flex flex-col gap-5">
        <ModuleHeader badges={<SourceBadge label="Polymarket" />} title="Expectativa de mercado" />

        <div className="flex flex-wrap gap-3">
          <IntervalSelector
            disabled={isFiltersLoading || hasError}
            onChange={(value) => setSelectedInterval(value as MarketExpectationInterval)}
            options={intervalOptions}
            value={selectedInterval}
          />

          <MultiSelect
            disabled={hasError}
            label="Candidatos"
            loading={isFiltersLoading}
            onChange={setSelectedCandidates}
            options={candidateOptions}
            value={selectedCandidates}
          />
        </div>

        <div className="flex flex-col gap-5 lg:flex-col-reverse">
          {chartFeedback ? (
            <div className="bg-navigation grid min-h-72 place-items-center rounded-md px-4 py-8 text-muted text-sm">
              {chartFeedback}
            </div>
          ) : (
            <PlaceholderChart
              imageAlt="Placeholder de gráfico temporal das probabilidades"
              imageSrc="/chart-placeholders/market-expectations.png"
              label="Placeholder de gráfico temporal das probabilidades"
              variant="line"
            />
          )}

          <div className="gap-3 grid md:grid-cols-4">
            <MetricCard text={currentLeaderText} title="Líder atual" value={currentLeaderValue} />

            <MetricCard title="Margem" value={leaderMarginValue} />

            <MetricCard
              text={largestChangeText}
              title="Maior variação"
              value={largestChangeValue}
              variant={largestChangeVariant}
            />

            <MetricCard text="Implementação futura" title="Evento recente" />
          </div>
        </div>
      </div>
    </ModulePanel>
  );
}
