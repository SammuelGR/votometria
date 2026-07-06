import AttentionMarketComparison from '~/pages/Dashboard/AttentionMarketComparison/AttentionMarketComparison';
import AttentionVsPolling from '~/pages/Dashboard/AttentionVsPolling/AttentionVsPolling';
import MarketExpectations from '~/pages/Dashboard/MarketExpectations/MarketExpectations';
import PublicAttention from '~/pages/Dashboard/PublicAttention/PublicAttention';
import ShareOfSearch from '~/pages/Dashboard/ShareOfSearch/ShareOfSearch';
import TseStateDistribution from '~/pages/Dashboard/TseStateDistribution/TseStateDistribution';

export default function Dashboard() {
  return (
    <section className="grid gap-5">
      <MarketExpectations />

      <PublicAttention />

      <AttentionVsPolling />

      <ShareOfSearch />

      <TseStateDistribution />

      <AttentionMarketComparison />
    </section>
  );
}
