import { useQuery } from '@tanstack/react-query';

import { fetchPollRows, type PollRow } from '~/services/pesquisas';

const PESQUISAS_QUERY_KEY = ['pesquisas'] as const;
const PESQUISAS_STALE_TIME = Infinity;

/** Loads the full electoral-poll gold table once and caches it. */
export function usePesquisas() {
  return useQuery<PollRow[]>({
    queryFn: fetchPollRows,
    queryKey: PESQUISAS_QUERY_KEY,
    staleTime: PESQUISAS_STALE_TIME,
  });
}
