import { useQuery } from '@tanstack/react-query';

import { fetchPollMonthlyRows, type PollMonthlyRow } from '~/services/pesquisasMensais';

const PESQUISAS_MENSAIS_QUERY_KEY = ['pesquisas-mensais'] as const;
const PESQUISAS_MENSAIS_STALE_TIME = Infinity;

/** Loads the full monthly-aggregated (multi-institution) poll gold table once and caches it. */
export function usePesquisasMensais() {
  return useQuery<PollMonthlyRow[]>({
    queryFn: fetchPollMonthlyRows,
    queryKey: PESQUISAS_MENSAIS_QUERY_KEY,
    staleTime: PESQUISAS_MENSAIS_STALE_TIME,
  });
}
