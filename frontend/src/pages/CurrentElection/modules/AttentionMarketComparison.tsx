import { CandidateSelector, ModuleHeader, ModulePanel, PlaceholderChart, SourceBadge } from '~/components/ui';
import { candidateOptions } from '~/pages/CurrentElection/modules/filterOptions';

export default function AttentionMarketComparison() {
  return (
    <ModulePanel>
      <div className="flex flex-col gap-5">
        <ModuleHeader
          badges={
            <>
              <SourceBadge label="Google Trends" />
              <SourceBadge label="Wikipedia" />
              <SourceBadge label="Polymarket" />
            </>
          }
          title="Atenção pública x expectativa de mercado"
        />

        <div className="flex flex-wrap gap-3">
          <CandidateSelector candidates={candidateOptions} label="Candidatos" value="all" />
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
