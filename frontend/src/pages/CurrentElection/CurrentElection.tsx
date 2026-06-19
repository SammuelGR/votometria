import AttentionMarketComparison from '~/pages/CurrentElection/modules/AttentionMarketComparison';
import MarketExpectations from '~/pages/CurrentElection/modules/MarketExpectations';
import PublicAttention from '~/pages/CurrentElection/modules/PublicAttention';
import ShareOfSearch from '~/pages/CurrentElection/modules/ShareOfSearch';

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
