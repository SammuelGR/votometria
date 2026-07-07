import { useMemo, useState } from 'react';

import PollsTimelineChart from '~/components/charts/PollsTimelineChart';
import {
  MetricCard,
  ModuleHeader,
  ModulePanel,
  MultiSelect,
  PlaceholderChart,
  SegmentedControl,
  SourceBadge,
} from '~/components/ui';
import { usePesquisasMensais } from '~/fetchers/hooks/usePesquisasMensais';
import type { ElectionYear } from '~/services/googleTrends';
import {
  candidatesByMean,
  filterPollMonthlyByYear,
  formatCandidateLabel,
  topPollCandidatesByMean,
} from '~/utils/pesquisasMensais';

const yearOptions = [
  { label: '2018', value: '2018' },
  { label: '2022', value: '2022' },
  { label: '2026', value: 'current' },
];

const INITIAL_SELECTED_CANDIDATE_LIMIT = 4;

export default function PollsTimeline() {
  const { data, isLoading, isError } = usePesquisasMensais();
  const [electionYear, setElectionYear] = useState<ElectionYear>('current');
  const [selection, setSelection] = useState<{ candidates: string[]; year: ElectionYear | null }>({
    candidates: [],
    year: null,
  });

  const rows = useMemo(() => filterPollMonthlyByYear(data ?? [], electionYear), [data, electionYear]);

  const orderedCandidates = useMemo(() => candidatesByMean(rows), [rows]);
  const candidateOptions = orderedCandidates.map((candidate) => ({
    label: formatCandidateLabel(candidate),
    value: candidate,
  }));
  const initialSelection = useMemo(() => topPollCandidatesByMean(rows, INITIAL_SELECTED_CANDIDATE_LIMIT), [rows]);
  const selectedValues = selection.year === electionYear ? selection.candidates : initialSelection;
  const selectedCandidates = selectedValues.length > 0 ? selectedValues : orderedCandidates;

  const topCandidate = orderedCandidates.find((candidate) => selectedCandidates.includes(candidate));

  function handleSelectionChange(candidates: string[]) {
    setSelection({ candidates, year: electionYear });
  }

  return (
    <ModulePanel>
      <div className="flex flex-col gap-5">
        <ModuleHeader
          badges={<SourceBadge label="Pesquisas eleitorais" tone="positive" />}
          title="Evolução das pesquisas eleitorais"
        />

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
        </div>

        {isLoading ? (
          <PlaceholderChart label="Carregando pesquisas eleitorais…" />
        ) : isError ? (
          <PlaceholderChart label="Falha ao carregar os dados. Verifique a planilha e o VITE_GOOGLE_SHEETS_ID." />
        ) : rows.length === 0 || selectedCandidates.length === 0 ? (
          <PlaceholderChart label="Selecione ao menos um candidato com dados no período." />
        ) : (
          <PollsTimelineChart candidates={selectedCandidates} rows={rows} />
        )}

        <div className="gap-3 grid sm:grid-cols-2">
          <MetricCard text={topCandidate ? formatCandidateLabel(topCandidate) : '—'} title="Maior média no período" />
        </div>
      </div>
    </ModulePanel>
  );
}
