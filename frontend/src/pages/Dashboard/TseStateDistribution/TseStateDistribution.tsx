import { useEffect, useState } from 'react';

import TseStateDistributionChart from '~/components/charts/TseStateDistributionChart';
import { ModuleHeader, ModulePanel, PlaceholderChart, SegmentedControl, SourceBadge } from '~/components/ui';
import {
  fetchTseStateDistributionRows,
  type TseStateDistRow,
  type TseStateDistTurn,
  type TseStateDistYear,
} from '~/services/tseStateDist';

const yearOptions = [
  { label: '2018', value: '2018' },
  { label: '2022', value: '2022' },
];

const turnOptions = [
  { label: '1º turno', value: 't1' },
  { label: '2º turno', value: 't2' },
];

export default function TseStateDistribution() {
  const [year, setYear] = useState<TseStateDistYear>('2022');
  const [turn, setTurn] = useState<TseStateDistTurn>('t2');
  const [rows, setRows] = useState<TseStateDistRow[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    let isActive = true;

    async function loadRows() {
      setIsLoading(true);
      setIsError(false);

      try {
        const nextRows = await fetchTseStateDistributionRows(year, turn);

        if (isActive) {
          setRows(nextRows);
        }
      } catch {
        if (isActive) {
          setIsError(true);
          setRows([]);
        }
      } finally {
        if (isActive) {
          setIsLoading(false);
        }
      }
    }

    void loadRows();

    return () => {
      isActive = false;
    };
  }, [year, turn]);

  return (
    <ModulePanel>
      <div className="flex flex-col gap-5">
        <ModuleHeader
          badges={
            <>
              <SourceBadge label="TSE" tone="neutral" />
            </>
          }
          title="Distribuição geográfica dos vencedores"
        />

        <div className="flex flex-wrap items-end gap-4">
          <SegmentedControl
            label="Eleição"
            onChange={(value) => setYear(value as TseStateDistYear)}
            options={yearOptions}
            value={year}
          />

          <SegmentedControl
            label="Turno"
            onChange={(value) => setTurn(value as TseStateDistTurn)}
            options={turnOptions}
            value={turn}
          />
        </div>

        <p className="font-mono text-[11px] text-muted">
          Mapa por estado destacando o candidato vencedor em cada UF para o turno selecionado.
        </p>

        {isLoading ? (
          <PlaceholderChart label="Carregando distribuição geográfica do TSE…" />
        ) : isError ? (
          <PlaceholderChart label="Falha ao carregar os dados. Verifique a planilha e o VITE_GOOGLE_SHEETS_ID." />
        ) : rows.length === 0 ? (
          <PlaceholderChart label="Sem dados disponíveis para esta combinação." />
        ) : (
          <TseStateDistributionChart rows={rows} />
        )}
      </div>
    </ModulePanel>
  );
}
