import { useEffect, useMemo, useState } from 'react';

import TseVotesChart from '~/components/charts/TseVotesChart';
import { MetricCard, ModuleHeader, ModulePanel, PlaceholderChart, SegmentedControl, SourceBadge } from '~/components/ui';
import { useTseVotes } from '~/fetchers/hooks/useTseVotes';
import { fetchTseComparisonRows, type TseComparisonRow } from '~/services/tseComparison';
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
  const [comparisonRows, setComparisonRows] = useState<TseComparisonRow[]>([]);
  const { data, isLoading, isError } = useTseVotes(electionYear, round);

  useEffect(() => {
    let isActive = true;

    async function loadComparisonRows() {
      try {
        const nextRows = await fetchTseComparisonRows(electionYear);

        if (isActive) {
          setComparisonRows(nextRows);
        }
      } catch {
        if (isActive) {
          setComparisonRows([]);
        }
      }
    }

    void loadComparisonRows();

    return () => {
      isActive = false;
    };
  }, [electionYear]);

  // Programação defensiva: criamos uma cópia do array [...data] e forçamos
  // a ordenação aqui para garantir que o topCandidate nunca quebre
  const rows = useMemo(() => {
    if (!data) return [];
    return [...data].sort((left, right) => right.votes - left.votes);
  }, [data]);

  const totalVotes = rows.reduce((sum, row) => sum + row.votes, 0);
  const topCandidate = rows[0]?.candidate ?? '—';
  const topVotes = rows[0]?.votes ?? 0;

  const firstComparison = useMemo(() => {
    if (rows.length === 0 || comparisonRows.length === 0) {
      return null;
    }

    const leader = rows[0];
    const comparisonRow = comparisonRows.find((row) => row.NM_URNA_CANDIDATO === leader?.candidate);

    if (!leader || !comparisonRow) {
      return null;
    }

    const firstTurnVotes = comparisonRow.QT_VOTOS_1T;
    const secondTurnVotes = comparisonRow.QT_VOTOS_2T;
    const deltaVotes = secondTurnVotes - firstTurnVotes;
    const deltaPercent = firstTurnVotes === 0 ? 0 : (deltaVotes / firstTurnVotes) * 100;

    return {
      candidate: leader.candidate,
      firstTurnVotes,
      secondTurnVotes,
      deltaVotes,
      deltaPercent,
    };
  }, [comparisonRows, rows]);

  const secondComparison = useMemo(() => {
    if (rows.length < 2 || comparisonRows.length === 0) {
      return null;
    }

    const runnerUp = rows[1];
    const comparisonRow = comparisonRows.find((row) => row.NM_URNA_CANDIDATO === runnerUp?.candidate);

    if (!runnerUp || !comparisonRow) {
      return null;
    }

    const firstTurnVotes = comparisonRow.QT_VOTOS_1T;
    const secondTurnVotes = comparisonRow.QT_VOTOS_2T;
    const deltaVotes = secondTurnVotes - firstTurnVotes;
    const deltaPercent = firstTurnVotes === 0 ? 0 : (deltaVotes / firstTurnVotes) * 100;

    return {
      candidate: runnerUp.candidate,
      firstTurnVotes,
      secondTurnVotes,
      deltaVotes,
      deltaPercent,
    };
  }, [comparisonRows, rows]);

  return (
    <ModulePanel>
      <div className="flex flex-col gap-5">
        <ModuleHeader badges={<SourceBadge label="TSE" tone="election" />} title="Votos válidos por candidato" />

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

        <div className="grid gap-3 sm:grid-cols-3">
          <MetricCard title="Votos válidos" value={totalVotes.toLocaleString('pt-BR')} />
          <MetricCard title="Líder" value={topCandidate ? `${topCandidate} · ${topVotes.toLocaleString('pt-BR')}` : '—'} />

          {firstComparison ? (
            <MetricCard
              title="Comparativo de turnos"
              text={
                <div className="space-y-4">
                  <div>
                    <p className="font-semibold text-foreground">
                      {firstComparison.candidate}
                    </p>
                    <p className="text-sm text-emerald-600">
                      {firstComparison.deltaVotes >= 0 ? '+' : ''}{firstComparison.deltaVotes.toLocaleString('pt-BR')} votos ({firstComparison.deltaPercent >= 0 ? '+' : ''}{firstComparison.deltaPercent.toLocaleString('pt-BR', { maximumFractionDigits: 1 })}%)
                    </p>
                  </div>
                  {secondComparison ? (
                    <div>
                      <p className="font-semibold text-foreground">
                        {secondComparison.candidate}
                      </p>
                      <p className="text-sm text-emerald-600">
                        {secondComparison.deltaVotes >= 0 ? '+' : ''}{secondComparison.deltaVotes.toLocaleString('pt-BR')} votos ({secondComparison.deltaPercent >= 0 ? '+' : ''}{secondComparison.deltaPercent.toLocaleString('pt-BR', { maximumFractionDigits: 1 })}%)
                      </p>
                    </div>
                  ) : null}
                </div>
              }
            />
          ) : (
            <MetricCard title="Comparativo de turnos" value="Sem comparação disponível" />
          )}
        </div>

        <p className="font-mono text-[11px] text-muted">
          Resultado oficial da apuração de votos válidos para o cargo presidencial, nos anos de 2018 e 2022.
        </p>
      </div>
    </ModulePanel>
  );
}