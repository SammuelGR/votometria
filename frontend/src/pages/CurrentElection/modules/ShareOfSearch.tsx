import {
  CandidateSelector,
  MetricCard,
  ModuleHeader,
  ModulePanel,
  PlaceholderChart,
  SourceBadge,
} from '~/components/ui';
import { candidateOptions } from '~/pages/CurrentElection/modules/filterOptions';

export default function ShareOfSearch() {
  return (
    <ModulePanel>
      <div className="flex h-full flex-col gap-5">
        <ModuleHeader badges={<SourceBadge label="Google Trends" />} title="Share of Search" />

        <div className="flex flex-wrap gap-3">
          <CandidateSelector candidates={candidateOptions} label="Candidatos" value="all" />
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
            <MetricCard label="Top 2" value="Implementação futura" />

            <MetricCard label="Maior participação" value="Implementação futura" />
          </div>
        </div>
      </div>
    </ModulePanel>
  );
}
