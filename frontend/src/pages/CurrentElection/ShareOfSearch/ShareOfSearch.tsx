import { MetricCard, ModuleHeader, ModulePanel, MultiSelect, PlaceholderChart, SourceBadge } from '~/components/ui';

export default function ShareOfSearch() {
  return (
    <ModulePanel>
      <div className="flex h-full flex-col gap-5">
        <ModuleHeader badges={<SourceBadge label="Google Trends" />} title="Share of Search" />

        <div className="flex flex-wrap gap-3">
          <MultiSelect label="Candidatos" onChange={() => {}} options={[]} value={[]} />
        </div>

        <div className="flex flex-col gap-5 lg:flex-col-reverse">
          <PlaceholderChart
            className="min-h-56"
            imageAlt="Placeholder de gráfico proporcional"
            imageSrc="/chart-placeholders/share-of-search.png"
            label="Placeholder de gráfico proporcional"
            variant="bar"
          />

          <div className="gap-3 grid">
            <MetricCard text="Implementação futura" title="Top 2" />

            <MetricCard text="Implementação futura" title="Maior participação" />
          </div>
        </div>
      </div>
    </ModulePanel>
  );
}
