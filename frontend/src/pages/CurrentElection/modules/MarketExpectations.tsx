import {
  CandidateSelector,
  MetricCard,
  ModuleHeader,
  ModulePanel,
  PlaceholderChart,
  SegmentedControl,
  SourceBadge,
} from '~/components/ui';
import { candidateOptions, intervalOptions } from '~/pages/CurrentElection/modules/filterOptions';

export default function MarketExpectations() {
  return (
    <ModulePanel>
      <div className="flex flex-col gap-5">
        <ModuleHeader badges={<SourceBadge label="Polymarket" />} title="Expectativa de mercado" />

        <div className="flex flex-wrap gap-3">
          <SegmentedControl label="Intervalo" options={intervalOptions} value="1h" />

          <CandidateSelector candidates={candidateOptions} label="Candidatos" value="all" />
        </div>

        <div className="flex flex-col gap-5 lg:flex-col-reverse">
          <PlaceholderChart
            imageAlt="Placeholder de gráfico temporal das probabilidades"
            imageSrc="/chart-placeholders/market-expectations.png"
            label="Placeholder de gráfico temporal das probabilidades"
            variant="line"
          />

          <div className="gap-3 grid md:grid-cols-4">
            <MetricCard label="Líder atual" value="Implementação futura" />

            <MetricCard label="Margem" value="Implementação futura" />

            <MetricCard label="Maior variação" value="Implementação futura" />

            <MetricCard label="Evento recente" value="Implementação futura" />
          </div>
        </div>
      </div>
    </ModulePanel>
  );
}
