import { useQuery } from '@tanstack/react-query';

import { getMarketExpectationOptions } from '~/fetchers/marketExpectations';
import { marketExpectationKeys } from '~/fetchers/hooks/marketExpectationKeys';

const MARKET_EXPECTATION_OPTIONS_STALE_TIME = 60 * 60 * 1000;

export function useMarketExpectationOptions() {
  return useQuery({
    queryFn: getMarketExpectationOptions,
    queryKey: marketExpectationKeys.options,
    staleTime: MARKET_EXPECTATION_OPTIONS_STALE_TIME,
  });
}
