import { useQuery } from '@tanstack/react-query';

import { marketExpectationKeys } from '~/fetchers/hooks/marketExpectationKeys';
import { getWeeklyMarketExpectations } from '~/fetchers/marketExpectations';

const WEEKLY_MARKET_EXPECTATIONS_STALE_TIME = Infinity;
const WEEKLY_MARKET_EXPECTATIONS_GC_TIME = Infinity;

type UseWeeklyMarketExpectationsOptions = {
  enabled?: boolean;
};

export function useWeeklyMarketExpectations(candidate: string | null, options?: UseWeeklyMarketExpectationsOptions) {
  return useQuery({
    enabled: (options?.enabled ?? true) && Boolean(candidate),
    gcTime: WEEKLY_MARKET_EXPECTATIONS_GC_TIME,
    queryFn: () => getWeeklyMarketExpectations(candidate ?? ''),
    queryKey: marketExpectationKeys.weeklyMarketExpectations(candidate),
    staleTime: WEEKLY_MARKET_EXPECTATIONS_STALE_TIME,
  });
}
