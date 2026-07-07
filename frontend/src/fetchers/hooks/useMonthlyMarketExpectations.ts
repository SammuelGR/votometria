import { useQuery } from '@tanstack/react-query';

import { marketExpectationKeys } from '~/fetchers/hooks/marketExpectationKeys';
import { getMonthlyMarketExpectations } from '~/fetchers/marketExpectations';

const MONTHLY_MARKET_EXPECTATIONS_STALE_TIME = Infinity;
const MONTHLY_MARKET_EXPECTATIONS_GC_TIME = Infinity;

type UseMonthlyMarketExpectationsOptions = {
  enabled?: boolean;
};

export function useMonthlyMarketExpectations(candidate: string | null, options?: UseMonthlyMarketExpectationsOptions) {
  return useQuery({
    enabled: (options?.enabled ?? true) && Boolean(candidate),
    gcTime: MONTHLY_MARKET_EXPECTATIONS_GC_TIME,
    queryFn: () => getMonthlyMarketExpectations(candidate ?? ''),
    queryKey: marketExpectationKeys.monthlyMarketExpectations(candidate),
    staleTime: MONTHLY_MARKET_EXPECTATIONS_STALE_TIME,
  });
}
