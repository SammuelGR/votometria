import { useMemo, useState } from 'react';

import AttentionVsPollingChart from '~/components/charts/AttentionVsPollingChart';
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
import { usePesquisas } from '~/fetchers/hooks/usePesquisas';
import type { ElectionYear, TrendsMetric } from '~/services/googleTrends';
import { buildAttentionVsPollingSeries } from '~/utils/attentionVsPolling';
import { filterByRange, filterByYear, termsByMean, type DateRange } from '~/utils/trends';

const yearOptions = [
  { label: '2018', value: '2018' },
  { label: '2022', value: '2022' },
  { label: '2026', value: 'current' },
];

const EMPTY_RANGE: DateRange = {};
const METRIC: TrendsMetric = 'interestRaw';

export default function AttentionVsPolling() {
  const trends = useGoogleTrends();
  const polls = usePesquisas();

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
  const scopedTrendsRows = useMemo(() => filterByRange(yearTrendsRows, range), [yearTrendsRows, range]);
  const orderedTerms = useMemo(() => termsByMean(scopedTrendsRows, METRIC), [scopedTrendsRows]);
  const candidateOptions = orderedTerms.map((term) => ({ label: term, value: term }));

  const activeCandidate =
    selection.year === electionYear && selection.candidate ? selection.candidate : (orderedTerms[0] ?? null);

  const points = useMemo(() => {
    if (!activeCandidate) {
      return [];
    }

    return buildAttentionVsPollingSeries(
      trends.data ?? [],
      polls.data ?? [],
      activeCandidate,
      electionYear,
      METRIC,
      range,
    );
  }, [trends.data, polls.data, activeCandidate, electionYear, range]);

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

              <SourceBadge label="Datafolha" tone="market" />
            </>
          }
          title="Atenção pública × pesquisa eleitoral"
        />

        <p className="font-mono text-[11px] text-muted">
          Compara o interesse de busca no Google Trends com o percentual do candidato nas pesquisas eleitorais
          (Datafolha) ao longo do tempo.
        </p>

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
          <AttentionVsPollingChart candidate={activeCandidate} points={points} year={electionYear} />
        )}

        <div className="flex flex-col gap-1">
          <p className="font-mono text-[11px] text-muted">
            Eixo único de 0 a 100%: índice relativo de atenção (Google Trends) e percentual de intenção nas pesquisas
            (Datafolha). Para comparar o mesmo período, a linha de atenção é recortada à janela coberta pelas pesquisas
            do candidato (da primeira à última data). Quando há mais de uma pesquisa na mesma data, usa-se a média do
            percentual. Datas sem pesquisa não viram zero — a linha de pesquisa apenas não pontua ali. Nenhum valor é
            reescalado ou interpolado.
          </p>

          {!hasPolls && activeCandidate ? (
            <p className="font-mono text-[11px] text-muted">
              Sem pesquisas Datafolha para “{activeCandidate}” neste recorte; apenas a atenção pública é exibida.
            </p>
          ) : null}
        </div>
      </div>
    </ModulePanel>
  );
}
