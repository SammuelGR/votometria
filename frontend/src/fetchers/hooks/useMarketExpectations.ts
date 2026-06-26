import { keepPreviousData, useQuery } from '@tanstack/react-query';

import { getMarketExpectations, type MarketExpectationsParams } from '~/fetchers/marketExpectations';
import { marketExpectationKeys } from '~/fetchers/hooks/marketExpectationKeys';

const MARKET_EXPECTATIONS_STALE_TIME = 60 * 60 * 1000;

type UseMarketExpectationsOptions = {
  enabled?: boolean;
};

export function useMarketExpectations(params?: MarketExpectationsParams, options?: UseMarketExpectationsOptions) {
  return useQuery({
    enabled: options?.enabled ?? true,
    placeholderData: keepPreviousData,
    queryFn: () => getMarketExpectations(params),
    queryKey: marketExpectationKeys.marketExpectations(params),
    staleTime: MARKET_EXPECTATIONS_STALE_TIME,
  });
}
