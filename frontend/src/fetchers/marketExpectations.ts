import { fetcher } from '~/fetchers/fetcher';
import type {
  MarketExpectationInterval,
  MarketExpectationMetadata,
  MarketExpectationOptions,
  MarketExpectationSeries,
  MarketExpectationSummary,
} from '~/models/marketExpectations';

type MarketExpectationOptionsResponse = MarketExpectationOptions;

export function getMarketExpectationOptions() {
  return fetcher<MarketExpectationOptionsResponse>('current-election/market-expectations/options');
}

type MarketExpectationsResponse = {
  metadata: MarketExpectationMetadata;
  series: MarketExpectationSeries[];
  sources: string[];
  summary: MarketExpectationSummary;
};

export type MarketExpectationsParams = {
  candidateCatalogIds?: number[];
  fromDate?: string;
  interval?: MarketExpectationInterval;
  toDate?: string;
};

export function getMarketExpectations(params?: MarketExpectationsParams) {
  return fetcher<MarketExpectationsResponse>('current-election/market-expectations', {
    queryParams: params,
  });
}
