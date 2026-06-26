export type MarketExpectationInterval = '1h' | '4h' | '1d' | '1w';

export type MarketExpectationDateRange = {
  max: string | null;
  min: string | null;
};

export type MarketExpectationOptionCandidate = {
  candidateCatalogId: number;
  displayName: string;
  latestProbability: number;
};

export type MarketExpectationOptions = {
  candidates: MarketExpectationOptionCandidate[];
  dateRange: MarketExpectationDateRange;
  defaultCandidateCatalogIds: number[];
  intervals: MarketExpectationInterval[];
};

export type MarketExpectationPoint = {
  probability: number;
  timestamp: string;
};

export type MarketExpectationSeries = {
  candidateCatalogId: number;
  candidateName: string;
  displayName: string;
  marketId: string;
  points: MarketExpectationPoint[];
};

export type MarketExpectationMetadata = {
  latestTimestamp: string | null;
};

export type MarketExpectationLeader = {
  candidateCatalogId: number;
  displayName: string;
  probability: number;
};

export type MarketExpectationLeaderMargin = {
  leaderCandidateCatalogId: number;
  runnerUpCandidateCatalogId: number;
  value: number;
};

export type MarketExpectationLargestChange = {
  absoluteValue: number;
  candidateCatalogId: number;
  displayName: string;
  value: number;
};

export type MarketExpectationSummary = {
  currentLeader: MarketExpectationLeader | null;
  largestChange: MarketExpectationLargestChange | null;
  leaderMargin: MarketExpectationLeaderMargin | null;
};
