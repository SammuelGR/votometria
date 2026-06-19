import {
  CandidateSelector,
  MetricCard,
  ModuleHeader,
  ModulePanel,
  PlaceholderChart,
  SourceBadge,
} from '~/components/ui';
import { candidateOptions } from '~/pages/CurrentElection/modules/filterOptions';

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
          <CandidateSelector candidates={candidateOptions} label="Candidatos" value="all" />
        </div>

        <div className="flex flex-col gap-5 lg:flex-col-reverse">
          <PlaceholderChart
            imageAlt="Placeholder de gráfico temporal de atenção pública"
            imageSrc="/chart-placeholders/public-attention.png"
            label="Placeholder de gráfico temporal de atenção pública"
          />

          <div className="gap-3 grid sm:grid-cols-2">
            <MetricCard label="Maior atenção" value="Implementação futura" />

            <MetricCard label="Maior pico" value="Implementação futura" />
          </div>
        </div>
      </div>
    </ModulePanel>
  );
}
