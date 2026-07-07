import AttentionMarketComparison from '~/pages/Dashboard/AttentionMarketComparison/AttentionMarketComparison';
import AttentionVsPolling from '~/pages/Dashboard/AttentionVsPolling/AttentionVsPolling';
import MarketExpectations from '~/pages/Dashboard/MarketExpectations/MarketExpectations';
import PublicAttention from '~/pages/Dashboard/PublicAttention/PublicAttention';
import ShareOfSearch from '~/pages/Dashboard/ShareOfSearch/ShareOfSearch';
import TseComparison from '~/pages/Dashboard/TseComparison/TseComparison';
import TseVotes from '~/pages/Dashboard/TseVotes/TseVotes';

export default function Dashboard() {
  return (
    <section className="grid gap-5">
      <MarketExpectations />

      <PublicAttention />

      <AttentionVsPolling />

      <ShareOfSearch />

      <TseComparison />

      <TseVotes />

      <AttentionMarketComparison />
    </section>
  );
}
