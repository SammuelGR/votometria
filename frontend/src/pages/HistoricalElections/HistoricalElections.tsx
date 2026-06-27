import { useState } from 'react';

import PublicAttentionModule from '~/components/modules/PublicAttentionModule';
import ShareOfSearchModule from '~/components/modules/ShareOfSearchModule';
import { SegmentedControl } from '~/components/ui';
import type { ElectionYear } from '~/services/googleTrends';

const yearOptions = [
  { label: '2018', value: '2018' },
  { label: '2022', value: '2022' },
];

export default function HistoricalElections() {
  const [year, setYear] = useState<ElectionYear>('2022');

  return (
    <section className="grid gap-5">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div className="flex flex-col gap-1">
          <span className="font-mono text-[11px] text-muted uppercase tracking-[0.12em]">Eleições passadas</span>

          <h1 className="font-semibold text-xl tracking-tight">Atenção pública em eleições anteriores</h1>
        </div>

        <SegmentedControl
          label="Eleição"
          onChange={(value) => setYear(value as ElectionYear)}
          options={yearOptions}
          value={year}
        />
      </div>

      <div className="grid gap-5 lg:grid-cols-[minmax(0,2fr)_minmax(280px,1fr)]">
        <PublicAttentionModule electionYear={year} />

        <ShareOfSearchModule electionYear={year} />
      </div>
    </section>
  );
}
