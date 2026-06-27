import { ModuleHeader, ModulePanel, MultiSelect, PlaceholderChart, SourceBadge } from '~/components/ui';

export default function AttentionMarketComparison() {
  return (
    <ModulePanel>
      <div className="flex flex-col gap-5">
        <ModuleHeader
          badges={
            <>
              <SourceBadge label="Google Trends" tone="attention" />
              <SourceBadge label="Polymarket" tone="market" />
            </>
          }
          title="Atenção pública × expectativa de mercado"
        />

        <div className="flex flex-wrap gap-3">
          <MultiSelect label="Candidatos" onChange={() => {}} options={[]} value={[]} />
        </div>

        <PlaceholderChart
          imageAlt="Placeholder de dispersão entre Share of Search e probabilidade de mercado"
          imageSrc="/chart-placeholders/attention-market-comparison.png"
          label="Placeholder de dispersão entre Share of Search e probabilidade de mercado"
          variant="scatter"
        />
      </div>
    </ModulePanel>
  );
}
