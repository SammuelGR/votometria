import { useQuery } from '@tanstack/react-query';

import { fetchTseVotesRows, type TseElectionYear, type TseVoteRound, type TseVoteRow } from '~/services/tseVotes';

const TSE_VOTES_QUERY_KEY = (year: TseElectionYear, round: TseVoteRound) => ['tse-votes', year, round] as const;
const TSE_VOTES_STALE_TIME = Infinity;

export function useTseVotes(year: TseElectionYear, round: TseVoteRound) {
  return useQuery<TseVoteRow[]>({
    queryFn: () => fetchTseVotesRows(year, round),
    queryKey: TSE_VOTES_QUERY_KEY(year, round),
    staleTime: TSE_VOTES_STALE_TIME,
  });
}
