import { useQuery } from '@tanstack/react-query';

import { fetchTrendsMonthlyRows, type TrendsMonthlyRow } from '~/services/googleTrendsMonthly';

const GOOGLE_TRENDS_MONTHLY_QUERY_KEY = ['google-trends-monthly'] as const;
const GOOGLE_TRENDS_MONTHLY_STALE_TIME = Infinity;

/** Loads the month-aggregated Google Trends gold table once and caches it. */
export function useGoogleTrendsMonthly() {
  return useQuery<TrendsMonthlyRow[]>({
    queryFn: fetchTrendsMonthlyRows,
    queryKey: GOOGLE_TRENDS_MONTHLY_QUERY_KEY,
    staleTime: GOOGLE_TRENDS_MONTHLY_STALE_TIME,
  });
}
