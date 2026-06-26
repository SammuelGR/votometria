import { MetricCard, ModuleHeader, ModulePanel, MultiSelect, PlaceholderChart, SourceBadge } from '~/components/ui';

export default function PublicAttention() {
  return (
    <ModulePanel>
      <div className="flex flex-col gap-5">
        <ModuleHeader
          badges={
            <>
              <SourceBadge label="Google Trends" />
              <SourceBadge label="Wikipedia" />
            </>
          }
          title="Atenção pública"
        />

        <div className="flex flex-wrap gap-3">
          <MultiSelect label="Candidatos" onChange={() => {}} options={[]} value={[]} />
        </div>

        <div className="flex flex-col gap-5 lg:flex-col-reverse">
          <PlaceholderChart
            imageAlt="Placeholder de gráfico temporal de atenção pública"
            imageSrc="/chart-placeholders/public-attention.png"
            label="Placeholder de gráfico temporal de atenção pública"
          />

          <div className="gap-3 grid sm:grid-cols-2">
            <MetricCard text="Implementação futura" title="Maior atenção" />

            <MetricCard text="Implementação futura" title="Maior pico" />
          </div>
        </div>
      </div>
    </ModulePanel>
  );
}
