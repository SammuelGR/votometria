import { useMemo, useState } from 'react';

import TseVotesChart from '~/components/charts/TseVotesChart';
import { MetricCard, ModuleHeader, ModulePanel, PlaceholderChart, SegmentedControl, SourceBadge } from '~/components/ui';
import { useTseVotes } from '~/fetchers/hooks/useTseVotes';
import type { TseElectionYear, TseVoteRound } from '~/services/tseVotes';

const yearOptions = [
  { label: '2018', value: '2018' as const },
  { label: '2022', value: '2022' as const },
];

const roundOptions = [
  { label: '1º turno', value: '1' as const },
  { label: '2º turno', value: '2' as const },
];

export default function TseVotes() {
  const [electionYear, setElectionYear] = useState<TseElectionYear>('2022');
  const [round, setRound] = useState<TseVoteRound>('1');
  const { data, isLoading, isError } = useTseVotes(electionYear, round);

  // Programação defensiva: criamos uma cópia do array [...data] e forçamos 
  // a ordenação aqui para garantir que o topCandidate nunca quebre
  const rows = useMemo(() => {
    if (!data) return [];
    return [...data].sort((left, right) => right.votes - left.votes);
  }, [data]);

  const totalVotes = rows.reduce((sum, row) => sum + row.votes, 0);
  const topCandidate = rows[0]?.candidate ?? '—';
  const topVotes = rows[0]?.votes ?? 0;

  return (
    <ModulePanel>
      <div className="flex flex-col gap-5">
        <ModuleHeader badges={<SourceBadge label="TSE" tone="neutral" />} title="Votos válidos por candidato" />

        <div className="flex flex-wrap items-end gap-4">
          <SegmentedControl
            label="Eleição"
            onChange={(value) => setElectionYear(value as TseElectionYear)}
            options={yearOptions}
            value={electionYear}
          />

          <SegmentedControl
            label="Turno"
            onChange={(value) => setRound(value as TseVoteRound)}
            options={roundOptions}
            value={round}
          />
        </div>

        {isLoading ? (
          <PlaceholderChart label="Carregando dados do TSE..." />
        ) : isError ? (
          <PlaceholderChart label="Falha ao carregar os dados. Verifique a aba processada no Google Sheets." />
        ) : rows.length === 0 ? (
          <PlaceholderChart label="Sem dados para o período selecionado." />
        ) : (
          <TseVotesChart rows={rows} />
        )}

        <div className="gap-3 grid sm:grid-cols-2">
          <MetricCard title="Votos válidos" value={totalVotes.toLocaleString('pt-BR')} />
          <MetricCard title="Líder" value={topCandidate ? `${topCandidate} · ${topVotes.toLocaleString('pt-BR')}` : '—'} />
        </div>

        <p className="font-mono text-[11px] text-muted">
          Dados lidos diretamente das abas processadas do Google Sheets para o TSE, já em formato consolidado para o frontend.
        </p>
      </div>
    </ModulePanel>
  );
}