import { useQuery } from '@tanstack/react-query';

import { fetchTrendsRows, type TrendsRow } from '~/services/googleTrends';

const GOOGLE_TRENDS_QUERY_KEY = ['google-trends'] as const;
const GOOGLE_TRENDS_STALE_TIME = Infinity;

/** Loads the full Google Trends long table once and caches it. */
export function useGoogleTrends() {
  return useQuery<TrendsRow[]>({
    queryFn: fetchTrendsRows,
    queryKey: GOOGLE_TRENDS_QUERY_KEY,
    staleTime: GOOGLE_TRENDS_STALE_TIME,
  });
}
