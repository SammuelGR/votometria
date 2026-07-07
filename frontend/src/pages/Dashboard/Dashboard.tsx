import ElectoralPanorama from '~/pages/Dashboard/ElectoralPanorama/ElectoralPanorama';
import MarketExpectations from '~/pages/Dashboard/MarketExpectations/MarketExpectations';
import PollsTimeline from '~/pages/Dashboard/PollsTimeline/PollsTimeline';
import PublicAttention from '~/pages/Dashboard/PublicAttention/PublicAttention';
import ShareOfSearch from '~/pages/Dashboard/ShareOfSearch/ShareOfSearch';
import TseVotes from '~/pages/Dashboard/TseVotes/TseVotes';

export default function Dashboard() {
  return (
    <section className="grid gap-5">
      <ElectoralPanorama />

      <MarketExpectations />

      <PublicAttention />

      <PollsTimeline />

      <ShareOfSearch />

      <TseVotes />
    </section>
  );
}
