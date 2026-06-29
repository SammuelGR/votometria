import { useState } from 'react';

import { IntervalSelector, MetricCard, ModuleHeader, ModulePanel, MultiSelect, SourceBadge } from '~/components/ui';
import { useMarketExpectationOptions } from '~/fetchers/hooks/useMarketExpectationOptions';
import { useMarketExpectations } from '~/fetchers/hooks/useMarketExpectations';
import type { MarketExpectationInterval } from '~/models/marketExpectations';
import { EMPTY_VALUE, formatProbability } from '~/utils/format';
import MarketExpectationsChart from './MarketExpectationsChart';

const DEFAULT_INTERVALS: MarketExpectationInterval[] = ['1h', '4h', '1d', '1w'];

const INTERVAL_LABELS: Partial<Record<MarketExpectationInterval, string>> = {
  '1w': '1 sem.',
};

export default function MarketExpectations() {
  const [selectedCandidates, setSelectedCandidates] = useState<string[]>();
  const [selectedInterval, setSelectedInterval] = useState<MarketExpectationInterval>('1h');

  const optionsQuery = useMarketExpectationOptions();

  const defaultCandidateValues = optionsQuery.data?.defaultCandidateCatalogIds.map(String);
  const selectedCandidateValues = selectedCandidates ?? defaultCandidateValues ?? [];
  const selectedCandidateCatalogIds = selectedCandidateValues
    .map(Number)
    .toSorted((firstId, secondId) => firstId - secondId);

  const marketExpectationsQuery = useMarketExpectations(
    {
      candidateCatalogIds: selectedCandidateCatalogIds?.length ? selectedCandidateCatalogIds : undefined,
      interval: selectedInterval,
    },
    {
      enabled: optionsQuery.isSuccess,
    },
  );

  const isOptionsLoading = optionsQuery.isLoading;
  const isSeriesLoading = marketExpectationsQuery.isLoading;
  const hasError = optionsQuery.isError || marketExpectationsQuery.isError;
  const isLoading = isOptionsLoading || isSeriesLoading;
  const hasSeries = (marketExpectationsQuery.data?.series.length ?? 0) > 0;
  const series = marketExpectationsQuery.data?.series ?? [];

  const candidateOptions =
    optionsQuery.data?.candidates.map((candidate) => ({
      label: candidate.displayName,
      value: String(candidate.candidateCatalogId),
    })) ?? [];

  const intervals = optionsQuery.data?.intervals ?? DEFAULT_INTERVALS;
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
        <ModuleHeader badges={<SourceBadge label="Polymarket" tone="market" />} title="Expectativa de mercado" />

        <div className="flex flex-wrap items-end gap-4">
          <IntervalSelector
            disabled={isOptionsLoading || hasError}
            onChange={(value) => setSelectedInterval(value as MarketExpectationInterval)}
            options={intervalOptions}
            value={selectedInterval}
          />

          <MultiSelect
            disabled={hasError}
            label="Candidatos"
            loading={isOptionsLoading}
            onChange={setSelectedCandidates}
            options={candidateOptions}
            value={selectedCandidateValues}
          />
        </div>

        <div className="flex flex-col gap-5 lg:flex-col-reverse">
          {chartFeedback ? (
            <div className="bg-navigation grid min-h-72 place-items-center rounded-md px-4 py-8 text-muted text-sm">
              {chartFeedback}
            </div>
          ) : (
            <MarketExpectationsChart interval={selectedInterval} series={series} />
          )}

          <div className="gap-3 grid sm:grid-cols-2 xl:grid-cols-4">
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
