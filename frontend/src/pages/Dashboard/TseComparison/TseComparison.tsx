import { useEffect, useState } from 'react';

import TseComparisonChart from '~/components/charts/TseComparisonChart';
import { ModuleHeader, ModulePanel, PlaceholderChart, SegmentedControl, SourceBadge } from '~/components/ui';
import { fetchTseComparisonRows, type TseComparisonRow, type TseComparisonYear } from '~/services/tseComparison';

const yearOptions = [
  { label: '2018', value: '2018' },
  { label: '2022', value: '2022' },
];

export default function TseComparison() {
  const [rows, setRows] = useState<TseComparisonRow[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isError, setIsError] = useState(false);
  const [year, setYear] = useState<TseComparisonYear>('2022');

  useEffect(() => {
    let isActive = true;

    async function loadRows() {
      setIsLoading(true);
      setIsError(false);

      try {
        const nextRows = await fetchTseComparisonRows(year);

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
  }, [year]);

  return (
    <ModulePanel>
      <div className="flex flex-col gap-5">
        <ModuleHeader
          badges={
            <>
              <SourceBadge label="TSE" tone="neutral" />
            </>
          }
          title="Comparativo de votos por turno"
        />

        <div className="flex flex-wrap items-end gap-4">
          <SegmentedControl
            label="Eleição"
            onChange={(value) => setYear(value as TseComparisonYear)}
            options={yearOptions}
            value={year}
          />
        </div>

        <p className="font-mono text-[11px] text-muted">
          Compara os votos dos candidatos no primeiro e no segundo turno para as eleições presidenciais.
        </p>

        {isLoading ? (
          <PlaceholderChart label="Carregando dados do TSE…" />
        ) : isError ? (
          <PlaceholderChart label="Falha ao carregar os dados. Verifique a planilha e o VITE_GOOGLE_SHEETS_ID." />
        ) : rows.length === 0 ? (
          <PlaceholderChart label="Sem dados disponíveis para esta eleição." />
        ) : (
          <TseComparisonChart rows={rows} />
        )}
      </div>
    </ModulePanel>
  );
}
