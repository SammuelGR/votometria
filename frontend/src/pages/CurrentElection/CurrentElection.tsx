import AttentionMarketComparison from '~/pages/CurrentElection/AttentionMarketComparison/AttentionMarketComparison';
import MarketExpectations from '~/pages/CurrentElection/MarketExpectations/MarketExpectations';
import PublicAttention from '~/pages/CurrentElection/PublicAttention/PublicAttention';
import ShareOfSearch from '~/pages/CurrentElection/ShareOfSearch/ShareOfSearch';

export default function CurrentElection() {
  return (
    <section className="grid gap-5">
      <MarketExpectations />

      <div className="grid gap-5 lg:grid-cols-[minmax(0,2fr)_minmax(280px,1fr)]">
        <PublicAttention />

        <ShareOfSearch />
      </div>

      <AttentionMarketComparison />
    </section>
  );
}
