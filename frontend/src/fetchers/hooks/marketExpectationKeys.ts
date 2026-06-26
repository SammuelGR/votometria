import type { MarketExpectationsParams } from '~/fetchers/marketExpectations';

export const marketExpectationKeys = {
  options: ['market-expectations', 'options'] as const,
  marketExpectations: (params?: MarketExpectationsParams) => ['market-expectations', params] as const,
};
